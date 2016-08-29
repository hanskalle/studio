#!/usr/bin/env python
from itertools import combinations


class Specials:
    def __init__(self):
        self.vars = []
        self.objective_terms = []
        self.constraints = []
        self.ignores = []

    def add_var(self, var):
        self.vars.append(var)

    def add_objective_term(self, term):
        self.objective_terms.append(term)

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def ignore_constraint(self, constraint):
        self.ignores.append(constraint)

    def get_objective_terms(self):
        terms = []
        for term in self.objective_terms:
            terms.append('+ ' + term)
        return terms


class Generator:
    def __init__(self, tasks, specials=Specials(), dont_exclude=None, fixes=None):
        self.tasks = tasks
        self.specials = specials
        self.dont_exclude = dont_exclude
        if fixes is not None:
            self.fixes = fixes
        else:
            self.fixes = []
        return

    def get_overrides(self):
        overrides = self.specials.ignores
        for constraint in self.specials.constraints:
            name = constraint.split()[2]
            if name[-1] == ':':
                name = name[:-1]
            overrides.append(name)
        return overrides

    @property
    def model(self):
        overrides = self.get_overrides()
        model = []
        for task in self.tasks:
            model.extend(task.get_sets())
        model.append('param first_week, integer;')
        model.append('param last_week, integer;')
        model.append('param number_of_weeks := last_week - first_week+1;')
        model.append('set weeks := first_week .. last_week;')
        for task in self.tasks:
            model.extend(task.get_params())
        for task in self.tasks:
            model.extend(task.get_vars())
        model.extend(self.specials.vars)
        model.append('minimize penalties:')
        for task in self.tasks:
            model.extend(task.get_objective_terms())
        model.extend(self.specials.get_objective_terms())
        model.append(';')
        for task in self.tasks:
            model.extend(task.get_rules(overrides))
        for task1, task2 in combinations(self.tasks, 2):
            if not ((task1.name, task2.name) in self.dont_exclude or (task2.name, task1.name) in self.dont_exclude):
                model.extend(task1.get_exclusion_rules(task2, overrides))
        model.extend(self.specials.constraints)
        model.extend(self.rules_for_fixes)
        for task in self.tasks:
            model.extend(task.get_checks())
        model.append('solve;')
        for task in self.tasks:
            model.extend(task.get_display_lines())
        # model.extend(self.specials.displays, 'display')
        model.append('end;')
        return model

    @property
    def rules_for_fixes(self):
        rules = []
        for i, fix in enumerate(self.fixes):
            rules.append("subject to fix_%d:" % i + " %s['%s',%s] = 1;" % fix)
        return rules

    @property
    def data(self):
        data = []
        for task in self.tasks:
            data.extend(task.get_data())
        return data

    def write(self, modelname, dataname):
        self.write_model(modelname)
        self.write_data(dataname)

    def write_model(self, filename):
        with open(filename, 'w') as f:
            for line in self.model:
                f.write(line)
                f.write('\n')

    def write_data(self, filename):
        with open(filename, 'w') as f:
            for line in self.data:
                f.write(line)
                f.write('\n')
            f.write('end;\n')
        return


class Task:
    def __init__(self, name, in_teams=False, paired_task=None, succesive_count=1, default_number_needed=1):
        self.name = name.replace(' ', '_')
        self.in_teams = in_teams
        self.params = {}
        # self.params = {
        #     'rather_not_penalty': 10,
        #     'offritme_penalty_L': 10,
        #     'offritme_penalty_M': 50,
        #     'offritme_penalty_H': 100,
        #     'offritme_penalty_X': 500}
        if paired_task is not None:
            self.paired_task = paired_task.replace(' ', '_')
            self.params['not_prefered_pair_penalty'] = 30
            self.prefered_pairs = []
        else:
            self.paired_task = None
            self.prefered_pairs = None
        self.succesive_count = succesive_count
        self.default_number_needed = default_number_needed
        self.dict = {
            'name': self.name,
            'paired_task': self.paired_task,
            'succesive_count': self.succesive_count,
            'default_number_needed': self.default_number_needed}
        if in_teams:
            self.dict['set'] = 'leaders'
            self.teams = {}
        else:
            self.dict['set'] = 'persons'
            self.teams = None
        self.number_needed = {}
        self.essential = {}

    def set_param(self, param, value):
        self.params[param] = value

    def set_number_needed(self, week, value):
        self.number_needed[week] = value

    def set_essential(self, person, value):
        assert self.in_teams
        self.essential[person] = value

    def set_team(self, team, persons):
        assert self.in_teams
        self.teams[team] = persons

    def set_pair(self, leader, helper):
        assert self.paired_task
        self.prefered_pairs.append((leader, helper))

    @staticmethod
    def matches_one_of(name, patterns):
        from re import match
        for pattern in patterns:
            if match(pattern, name):
                return True
        return False

    def get_sets(self):
        sets = ['set %(name)s_persons;' % self.dict]
        if self.in_teams:
            sets.append('set %(name)s_teams;' % self.dict)
        return sets

    def get_params(self):
        params = ['param %(name)s_offritme_penalty_L, >=0, default 10;' % self.dict,
                  'param %(name)s_offritme_penalty_M, >=0, default 50;' % self.dict,
                  'param %(name)s_offritme_penalty_H, >=0, default 100;' % self.dict,
                  'param %(name)s_offritme_penalty_X, >=0, default 500;' % self.dict,
                  'param %(name)s_rather_not_penalty, >=0, default 10;' % self.dict,
                  'param %(name)s_available {p in %(name)s_persons, w in weeks}, >=0, <=1, default 1;' % self.dict,
                  'param %(name)s_number_needed {w in weeks}, integer, >=0, default %(default_number_needed)d;' % self.dict]
        if self.in_teams:
            params.append('set %(name)s_leaders;' % self.dict)
            params.append('set %(name)s_team {l in %(name)s_leaders};' % self.dict)
            params.append('param %(name)s_essential {p in %(name)s_persons}, >= 0, default 0;' % self.dict)
            params.append('param %(name)s_team_available {l in %(name)s_leaders, w in weeks} := ' % self.dict)
            params.append(
                '  (min {p in %(name)s_team[l]: %(name)s_essential[p]=0} %(name)s_available[p,w]);' % self.dict)
        if self.paired_task is not None:
            params.append(
                'param %(name)s_prefered_pair {p1 in %(paired_task)s_persons, p2 in %(name)s_persons}, '
                'binary, default 0;' % self.dict)
            params.append('param %(name)s_ritme {p in %(name)s_persons}, >=1;' % self.dict)
            params.append('param %(name)s_min {p in %(name)s_persons}, integer, >=0, '
                          'default %(succesive_count)d * floor((sum {w in weeks} %(name)s_number_needed[w])'
                          '/ %(default_number_needed)d / %(succesive_count)d / %(name)s_ritme[p]);' % self.dict)
            params.append('param %(name)s_max {p in %(name)s_persons}, integer, >=0, '
                          'default %(succesive_count)d * ceil((sum {w in weeks} %(name)s_number_needed[w])'
                          '/ %(default_number_needed)d / %(succesive_count)d / %(name)s_ritme[p]);' % self.dict)
            params.append('param %(name)s_not_prefered_pair_penalty, >=0, default 30;' % self.dict)
        else:
            params.append('param %(name)s_ritme {p in %(name)s_persons}, >=1;' % self.dict)
            params.append('param %(name)s_min {p in %(name)s_persons}, integer, >=0, '
                          'default %(succesive_count)d * '
                          'floor(number_of_weeks / %(succesive_count)d / %(name)s_ritme[p]);' % self.dict)
            params.append('param %(name)s_max {p in %(name)s_persons}, integer, >=0, '
                          'default %(succesive_count)d * '
                          'ceil(number_of_weeks / %(succesive_count)d / %(name)s_ritme[p]);' % self.dict)
            params.append(
                'param %(name)s_last {x in %(name)s_persons}, integer, < first_week, default -100;' % self.dict)
        return params

    def get_vars(self):
        variables = [
            'var %(name)s {t in %(name)s_%(set)s, w in weeks}, binary;' % self.dict,
            'var %(name)s_rather_not {p in %(name)s_persons, w in weeks}, binary;' % self.dict]
        if self.in_teams:
            variables.append('var %(name)s_missing {p in %(name)s_persons, w in weeks}, binary;' % self.dict)
            variables.append('var %(name)s_present {p in %(name)s_persons, w in weeks}, binary;' % self.dict)
        if self.paired_task is not None:
            variables.append('var %(name)s_not_prefered_pair {w in weeks}, binary;' % self.dict)
        else:
            variables.extend([
                'var %(name)s_offritme_L {t in %(name)s_%(set)s, w in weeks}, integer, >=0;' % self.dict,
                'var %(name)s_offritme_M {t in %(name)s_%(set)s, w in weeks}, integer, >=0;' % self.dict,
                'var %(name)s_offritme_H {t in %(name)s_%(set)s, w in weeks}, integer, >=0;' % self.dict,
                'var %(name)s_offritme_X {t in %(name)s_%(set)s, w in weeks}, integer, >=0;' % self.dict])
        return variables

    def get_objective_terms(self):
        terms = ['  + (sum {p in %(name)s_persons, w in weeks}' % self.dict,
                 '    %(name)s_rather_not_penalty * %(name)s_rather_not[p,w])' % self.dict]
        if self.in_teams:
            terms.append('  + (sum {p in %(name)s_persons, w in weeks}' % self.dict)
            terms.append('    %(name)s_essential[p] * %(name)s_missing[p,w])' % self.dict)
        if self.paired_task is None:
            terms.append('  + (sum {x in %(name)s_%(set)s, w in weeks}' % self.dict)
            terms.append('    %(name)s_offritme_penalty_L * %(name)s_offritme_L[x,w])' % self.dict)
            terms.append('  + (sum {x in %(name)s_%(set)s, w in weeks}' % self.dict)
            terms.append('    %(name)s_offritme_penalty_M * %(name)s_offritme_M[x,w])' % self.dict)
            terms.append('  + (sum {x in %(name)s_%(set)s, w in weeks}' % self.dict)
            terms.append('    %(name)s_offritme_penalty_H * %(name)s_offritme_H[x,w])' % self.dict)
            terms.append('  + (sum {x in %(name)s_%(set)s, w in weeks}' % self.dict)
            terms.append('    %(name)s_offritme_penalty_X * %(name)s_offritme_X[x,w])' % self.dict)
        else:
            terms.append('  + (sum {w in weeks}')
            terms.append('    %(name)s_not_prefered_pair_penalty * %(name)s_not_prefered_pair[w])' % self.dict)
        return terms

    def get_rules(self, overrides):
        rules = []
        rules.extend(self.get_rule_number_needed(overrides))
        rules.extend(self.get_rule_available(overrides))
        rules.extend(self.get_rule_minimum(overrides))
        rules.extend(self.get_rule_maximum(overrides))
        if self.in_teams:
            rules.extend(self.get_rule_missing(overrides))
            rules.extend(self.get_rule_present(overrides))
        if self.paired_task is None:
            rules.extend(self.get_rule_ritme(overrides))
            rules.extend(self.get_rule_ritme_history(overrides))
        else:
            rules.extend(self.get_rule_prefered_pair(overrides))
        if self.succesive_count == 2:
            rules.extend(self.get_rule_twice(overrides))
        return rules

    def get_data(self):
        data = []
        if len(self.params):
            for param, value in self.params.items():
                if type(value) is dict:
                    data.append('param %s_%s :=' % (self.dict['name'], param))
                    for label, single_value in value.items():
                        data.append('  %s %s' % (label, single_value))
                    data.append(';')
                elif type(value) is int:
                    data.append('param %s_%s := %d;' % (self.dict['name'], param, value))
                elif type(value) is float:
                    data.append('param %s_%s := %f;' % (self.dict['name'], param, value))
        if len(self.number_needed):
            data.append('param %(name)s_number_needed :=' % self.dict)
            for week, numberneeded in self.number_needed.items():
                data.append('  %d %d' % (week, numberneeded))
            data.append(';')
        if len(self.essential):
            data.append('param %(name)s_essential :=' % self.dict)
            for person, value in self.essential.items():
                data.append('  %s %d' % (person, value))
            data.append(';')
        if self.in_teams:
            data.append('set %(name)s_leaders := ' % self.dict + ' '.join(self.teams.keys()) + ';')
            for team, persons in self.teams.items():
                data.append('set %s_team[%s] := %s;' % (self.dict['name'], team, ' '.join(persons)))
        if self.prefered_pairs and len(self.prefered_pairs):
            data.append('param %(name)s_prefered_pair := ' % self.dict)
            for pair in self.prefered_pairs:
                data.append('  %s %s 1' % pair)
            data.append(';')
        return data

    def get_exclusion_rules(self, other_task, overrides):
        rules = []
        if not self.matches_one_of('%s_excludes_%s' % (self.name, other_task.name), overrides):
            rules.append('subject to %s_excludes_%s' % (self.name, other_task.name))
            generator = ('  {w in weeks, p in %s_persons inter %s_persons' % (self.name, other_task.name))
            if self.in_teams:
                generator += ', l1 in %s_leaders' % self.name
            if other_task.in_teams:
                generator += ', l2 in %s_leaders' % other_task.name
            if self.in_teams or other_task.in_teams:
                generator += ': '
            if self.in_teams:
                generator += '(p in %s_team[l1])' % self.name
            if self.in_teams and other_task.in_teams:
                generator += ' and '
            if other_task.in_teams:
                generator += '(p in %s_team[l2])' % other_task.name
            generator += '}:'
            rules.append(generator)
            if self.in_teams:
                expression = '  %s[l1,w]' % self.name
            else:
                expression = '  %s[p,w]' % self.name
            if other_task.in_teams:
                expression += ' + %s[l2,w]' % other_task.name
            else:
                expression += ' + %s[p,w]' % other_task.name
            expression += ' <= 1;'
            rules.append(expression)
        return rules

    def get_rule_number_needed(self, overrides):
        rules = []
        if not self.matches_one_of('number_needed_%(name)s' % self.dict, overrides):
            rules.append('subject to number_needed_%(name)s' % self.dict)
            rules.append('  {w in weeks}:')
            rules.append('  (sum {x in %(name)s_%(set)s} %(name)s[x,w])' % self.dict)
            #            rules.append('    + %(name)s_empty[w]' % self.dict)
            rules.append('    = %(name)s_number_needed[w];' % self.dict)
        return rules

    def get_rule_available(self, overrides):
        rules = []
        if not self.matches_one_of('available_%(name)s' % self.dict, overrides):
            rules.append('subject to available_%(name)s' % self.dict)
            rules.append('  {w in weeks, p in %(name)s_%(set)s}:' % self.dict)
            if self.in_teams:
                rules.append(
                    '  %(name)s[p,w] <= %(name)s_team_available[p,w] + 0.5 * %(name)s_rather_not[p,w];' % self.dict)
            else:
                rules.append('  %(name)s[p,w] <= %(name)s_available[p,w] + 0.5 * %(name)s_rather_not[p,w];' % self.dict)
        return rules

    def get_rule_ritme(self, overrides):
        rules = []
        if not self.matches_one_of('ritme_%(name)s' % self.dict, overrides):
            rules.append('subject to ritme_%(name)s_L' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s, w in first_week+(floor(%(name)s_ritme[p])-1)..last_week: floor(%(name)s_ritme[p]) >= 2}:' % self.dict)
            rules.append(
                '  %(name)s[p,w] + %(name)s[p,w-(floor(%(name)s_ritme[p])-1)] <= 1 + %(name)s_offritme_L[p,w];' % self.dict)
            rules.append('subject to ritme_%(name)s_M' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s, w in first_week+(floor(%(name)s_ritme[p])-2)..last_week: floor(%(name)s_ritme[p]) >= 3}:'
                % self.dict)
            rules.append(
                '  %(name)s[p,w] + %(name)s[p,w-(floor(%(name)s_ritme[p])-2)] <= 1 + %(name)s_offritme_M[p,w];' % self.dict)
            rules.append('subject to ritme_%(name)s_H' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s, d in floor(%(name)s_ritme[p]/3)+1..floor(%(name)s_ritme[p]-3), w in first_week+d..last_week: %(name)s_ritme[p] >= 5}:'
                % self.dict)
            rules.append('  %(name)s[p,w] + %(name)s[p,w-d] <= 1 + %(name)s_offritme_H[p,w];' % self.dict)
            rules.append('subject to ritme_%(name)s_X' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s, d in 1..floor(%(name)s_ritme[p]/3), w in first_week+d..last_week: %(name)s_ritme[p] >= 4}:'
                % self.dict)
            rules.append('  %(name)s[p,w] + %(name)s[p,w-d] <= 1 + %(name)s_offritme_X[p,w];' % self.dict)
        return rules

    def get_rule_ritme_history(self, overrides):
        rules = []
        if not self.matches_one_of('ritme_history_%(name)s' % self.dict, overrides):
            rules.append('subject to ritme_history_%(name)s_L' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s: floor(%(name)s_ritme[p]) >= 2 and %(name)s_last[p]+floor(%(name)s_ritme[p])-1 in weeks}:' % self.dict)
            rules.append(
                '  %(name)s[p,%(name)s_last[p]+floor(%(name)s_ritme[p])-1] <= %(name)s_offritme_L[p,%(name)s_last[p]+floor(%(name)s_ritme[p])-1];' % self.dict)
            rules.append('subject to ritme_history_%(name)s_M' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s: floor(%(name)s_ritme[p]) >= 3 and %(name)s_last[p]+floor(%(name)s_ritme[p])-2 in weeks}:' % self.dict)
            rules.append(
                '  %(name)s[p,%(name)s_last[p]+floor(%(name)s_ritme[p])-2] <= %(name)s_offritme_M[p,%(name)s_last[p]+floor(%(name)s_ritme[p])-2];' % self.dict)
            rules.append('subject to ritme_history_%(name)s_H' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s, d in floor(%(name)s_ritme[p]/3)+1..floor(%(name)s_ritme[p])-3: floor(%(name)s_ritme[p]) >= 5 and %(name)s_last[p]+d in weeks}:'
                % self.dict)
            rules.append('  %(name)s[p,%(name)s_last[p]+d] <= %(name)s_offritme_H[p,%(name)s_last[p]+d];' % self.dict)
            rules.append('subject to ritme_history_%(name)s_X' % self.dict)
            rules.append(
                '  {p in %(name)s_%(set)s, d in 1..floor(%(name)s_ritme[p]/3): floor(%(name)s_ritme[p]) >= 5 and %(name)s_last[p]+d in weeks}:'
                % self.dict)
            rules.append('  %(name)s[p,%(name)s_last[p]+d] <= %(name)s_offritme_X[p,%(name)s_last[p]+d];' % self.dict)
        return rules

    def get_rule_minimum(self, overrides):
        rules = []
        if not self.matches_one_of('minimum_%(name)s' % self.dict, overrides):
            rules.append('subject to minimum_%(name)s' % self.dict)
            rules.append('  {p in %(name)s_%(set)s}:' % self.dict)
            rules.append('  (sum {w in weeks} %(name)s[p,w])' % self.dict)
            rules.append('    >= %(name)s_min[p];' % self.dict)
        return rules

    def get_rule_maximum(self, overrides):
        rules = []
        if not self.matches_one_of('maximum_%(name)s' % self.dict, overrides):
            rules.append('subject to maximum_%(name)s' % self.dict)
            rules.append('  {p in %(name)s_%(set)s}:' % self.dict)
            rules.append('  (sum {w in weeks} %(name)s[p,w])' % self.dict)
            rules.append('    <= %(name)s_max[p];' % self.dict)
        return rules

    def get_rule_prefered_pair(self, overrides):
        rules = []
        if not self.matches_one_of('prefered_pair_%(name)s' % self.dict, overrides):
            rules.append('subject to prefered_pair_%(name)s' % self.dict)
            rules.append('  {w in weeks, p1 in %(paired_task)s_persons, p2 in %(name)s_persons}:' % self.dict)
            rules.append(
                '  %(paired_task)s[p1,w] + %(name)s[p2,w] <= '
                '1 + %(name)s_prefered_pair[p1,p2] + %(name)s_not_prefered_pair[w];' % self.dict)
        return rules

    def get_rule_missing(self, overrides):
        rules = []
        if not self.matches_one_of('missing_%(name)s' % self.dict, overrides):
            rules.append('subject to missing_%(name)s' % self.dict)
            rules.append('  {w in weeks, l in %(name)s_leaders, p in %(name)s_team[l]}:' % self.dict)
            rules.append('  %(name)s[l,w] <= %(name)s_available[p,w] + %(name)s_missing[p,w];' % self.dict)
        return rules

    def get_rule_present(self, overrides):
        rules = []
        if not self.matches_one_of('present_%(name)s' % self.dict, overrides):
            rules.append('subject to present_%(name)s' % self.dict)
            rules.append(
                '  {w in weeks, p in %(name)s_persons}:' % self.dict)
            rules.append(
                '  (sum {l in %(name)s_leaders: p in %(name)s_team[l]} %(name)s[l,w]) = %(name)s_present[p,w] + %(name)s_missing[p,w];' % self.dict)
        return rules

    def get_rule_twice(self, overrides):
        rules = []
        if not self.matches_one_of('twice_%(name)s' % self.dict, overrides):
            rules.append('subject to twice_%(name)s' % self.dict)
            rules.append(
                '  {x in %(name)s_%(set)s, w in 0..(number_of_weeks/2-1): (first_week+2*w+1) in weeks}:' % self.dict)
            rules.append('  %(name)s[x,first_week+2*w] = %(name)s[x,first_week+2*w+1];' % self.dict)
        return rules

    def get_checks(self):
        checks = []
        if self.paired_task is None and not self.in_teams:
            checks.append(
                'check: (sum {p in %(name)s_%(set)s} (1 / %(name)s_ritme[p])) >= (sum {w in weeks} %(name)s_number_needed[w]) / number_of_weeks - 0.5;' % self.dict)
            checks.append(
                'check: (sum {p in %(name)s_%(set)s} (1 / %(name)s_ritme[p])) <= (sum {w in weeks} %(name)s_number_needed[w]) / number_of_weeks + 0.5;' % self.dict)
        if self.in_teams:
            checks.append(
                'check {p in %(name)s_leaders}: (sum {w in weeks} %(name)s_available[p,w]) >= %(name)s_min[p];' % self.dict)
            checks.append(
                'check {w in weeks}: (sum {p in %(name)s_leaders} %(name)s_available[p,w]) >= %(name)s_number_needed[w];' % self.dict)
        else:
            checks.append(
                'check {p in %(name)s_persons}: (sum {w in weeks} %(name)s_available[p,w]) >= %(name)s_min[p];' % self.dict)
            checks.append(
                'check {w in weeks}: (sum {p in %(name)s_persons} %(name)s_available[p,w]) >= %(name)s_number_needed[w];' % self.dict)
        return checks

    def get_display_lines(self):
        lines = [
            'display %(name)s;' % self.dict,
            'display %(name)s_rather_not;' % self.dict]
        if self.in_teams:
            lines.append('display %(name)s_present;' % self.dict)
        if self.paired_task:
            lines.append('display %(name)s_not_prefered_pair;' % self.dict)
        else:
            lines.extend([
                'display %(name)s_offritme_L;' % self.dict,
                'display %(name)s_offritme_M;' % self.dict,
                'display %(name)s_offritme_H;' % self.dict,
                'display %(name)s_offritme_X;' % self.dict])
        return lines
