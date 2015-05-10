#!/usr/bin/env python
from itertools import combinations

class Task:
    def __init__(self,name,in_teams=False,paired_task=None,succesive_count=1):
        self.succesive_count = succesive_count
        self.name = name.replace(' ','_')
        self.in_teams = in_teams
        if paired_task != None:
            self.paired_task = paired_task.replace(' ','_')
        else:
            self.paired_task = None
        self.dict = {'name': self.name, 'paired_task': self.paired_task, 'succesive_count': self.succesive_count}
        if in_teams:
            self.dict['set'] = "teams"
        else:
            self.dict['set'] = "persons"
            
    def get_sets(self):
        sets = []
        sets.append("set %(name)s_persons;" % self.dict)
        if self.in_teams:
            sets.append("set %(name)s_teams;" % self.dict)
        return sets

    def get_params(self):
        params = []
        params.append("param %(name)s_offritme_penalty, >=0;" % self.dict)
        params.append("param %(name)s_rather_not_penalty, >=0;" % self.dict)
        params.append("param %(name)s_available {p in %(name)s_persons, w in weeks}, >=0, <=1;" % self.dict)
        params.append("param %(name)s_number_needed {w in weeks}, integer, >=0;" % self.dict)
        params.append("param %(name)s_min {p in %(name)s_%(set)s}, integer, >=0;" % self.dict)
        params.append("param %(name)s_max {p in %(name)s_%(set)s}, integer, >=0;" % self.dict)
        if self.in_teams:
            params.append("param %(name)s_member {t in %(name)s_teams, p in %(name)s_persons}, binary;" % self.dict)
            params.append("param %(name)s_essential {p in %(name)s_persons}, >= 0;" % self.dict)
            params.append("param %(name)s_maximum_missing {t in %(name)s_teams}, >= 0;" % self.dict)
        if self.paired_task != None:
            params.append("param %(name)s_prefered_pair {p1 in %(paired_task)s_persons, p2 in %(name)s_persons}, binary;" % self.dict)
            params.append("param %(name)s_not_prefered_pair_penalty, >=0;" % self.dict)
        else:
            params.append("param %(name)s_ritme {p in %(name)s_%(set)s}, integer, >=1;" % self.dict)
            params.append("param %(name)s_rest {p in %(name)s_%(set)s}, integer, >=0;" % self.dict)
            params.append("param %(name)s_last {x in %(name)s_%(set)s}, integer, < first_week;" % self.dict)
        return params

    def get_vars(self):
        variables = []
        variables.append("var %(name)s {t in %(name)s_%(set)s, w in weeks}, binary;" % self.dict)
        variables.append("var %(name)s_rather_not {p in %(name)s_persons, w in weeks}, binary;" % self.dict)
        if self.in_teams:
            variables.append("var %(name)s_missing {p in %(name)s_persons, w in weeks}, binary;" % self.dict)
        if self.paired_task != None:
            variables.append("var %(name)s_not_prefered_pair {w in weeks}, binary;" % self.dict)
        else:
            variables.append("var %(name)s_offritme {t in %(name)s_%(set)s, w in weeks_extended}, binary;" % self.dict)
        return variables
        
    def get_objective_terms(self):
        terms = []
        terms.append("  + (sum {p in %(name)s_persons, w in weeks}" % self.dict)
        terms.append("    %(name)s_rather_not_penalty * %(name)s_rather_not[p,w])" % self.dict)
        if self.in_teams:
            terms.append("  + (sum {p in %(name)s_persons, w in weeks}" % self.dict)
            terms.append("    %(name)s_essential[p] * %(name)s_missing[p,w])" % self.dict)
        if self.paired_task == None:
            terms.append("  + (sum {x in %(name)s_%(set)s, w in weeks_extended}" % self.dict)
            terms.append("    %(name)s_offritme_penalty * %(name)s_offritme[x,w])" % self.dict)
        else:
            terms.append("  + (sum {w in weeks}")
            terms.append("    %(name)s_not_prefered_pair_penalty * %(name)s_not_prefered_pair[w])" % self.dict)
        return terms

    def get_rules(self):
        rules = []
        rules.extend(self.get_rule_number_needed())
        rules.extend(self.get_rule_available())
        rules.extend(self.get_rule_minimum())
        rules.extend(self.get_rule_maximum())
        if self.in_teams:
            rules.extend(self.get_rule_missing())
#            rules.extend(self.get_rule_maximum_missing())
        if self.paired_task == None:
            rules.extend(self.get_rule_ritme())
            rules.extend(self.get_rule_ritme_history())
            rules.extend(self.get_rule_rest())
            rules.extend(self.get_rule_rest_history())
        else:
            rules.extend(self.get_rule_prefered_pair())
        if self.succesive_count == 2:
            rules.extend(self.get_rule_twice())
        return rules
        
    def get_exclusion_rules(self, other_task):
        rules = []
        rules.append("subject to %s_excludes_%s" % (self.name, other_task.name))
        generator = ("  {w in weeks, p in %s_persons inter %s_persons" % (self.name, other_task.name))
        if self.in_teams:
            generator += ", t1 in %s_teams" % (self.name)
        if other_task.in_teams:
            generator += ", t2 in %s_teams" % (other_task.name)
        if self.in_teams or other_task.in_teams:
            generator += ": "
        if self.in_teams:
            generator += "%s_member[t1,p]=1" % (self.name)
        if self.in_teams and other_task.in_teams:
            generator += " and "
        if other_task.in_teams:
            generator += "%s_member[t2,p]=1" % (other_task.name)
        generator += "}:"
        rules.append(generator)        
        if self.in_teams:
            expression = "  %s[t1,w]" % (self.name)
        else:
            expression = "  %s[p,w]" % (self.name)
        if other_task.in_teams:
            expression += " + %s[t2,w]" % (other_task.name)
        else:
            expression += " + %s[p,w]" % (other_task.name)
        expression += (" <= 1;")
        rules.append(expression)
        return rules

    def get_rule_number_needed(self):
        rules = []
        rules.append("subject to number_needed_%(name)s" % self.dict)
        rules.append("  {w in weeks}:")
        rules.append("  (sum {x in %(name)s_%(set)s} %(name)s[x,w]) = %(name)s_number_needed[w];" % self.dict)
        return rules

    def get_rule_available(self):
        rules = []
        rules.append("subject to available_%(name)s" % self.dict)
        generator = "  {w in weeks, p in %(name)s_persons" % self.dict
        if self.in_teams:
            generator += ", t in %(name)s_teams: %(name)s_member[t,p]=1 and %(name)s_essential[p]=0" % self.dict
        generator += "}:"
        rules.append(generator)
        expression = "  %(name)s[" % self.dict
        if self.in_teams:
            expression += "t"
        else:
            expression += "p"
        expression += ",w] <= %(name)s_available[p,w] + 0.5 * %(name)s_rather_not[p,w];" % self.dict
        rules.append(expression)
        return rules

    def get_rule_ritme(self):
        rules = []
        rules.append("subject to ritme_%(name)s" % self.dict)
        rules.append("  {w1 in weeks_extended, x in %(name)s_%(set)s}:" % self.dict)
        rules.append("  (sum {w2 in w1..(w1 + %(name)s_ritme[x]-1): w2 in weeks} %(name)s[x,w2])" % self.dict)
        rules.append("    <= %(succesive_count)i + %(name)s_offritme[x,w1];" % self.dict)
        return rules

    def get_rule_ritme_history(self):
        rules = []
        rules.append("subject to ritme_history_%(name)s" % self.dict)
        rules.append("  {x in %(name)s_%(set)s, w1 in (first_week-%(name)s_ritme[x]+1)..%(name)s_last[x]}:" % self.dict)
        rules.append("  (sum {w2 in w1..(w1 + %(name)s_ritme[x]-1): w2 in weeks} %(name)s[x,w2])" % self.dict)
        rules.append("    <= %(name)s_offritme[x,w1];" % self.dict)
        return rules

    def get_rule_minimum(self):
        rules = []
        rules.append("subject to minimum_%(name)s" % self.dict)
        rules.append("  {x in %(name)s_%(set)s}:" % self.dict)
        rules.append("  (sum {w in weeks} %(name)s[x,w])" % self.dict)
        rules.append("    >= %(name)s_min[x];" % self.dict)
        return rules

    def get_rule_maximum(self):
        rules = []
        rules.append("subject to maximum_%(name)s" % self.dict)
        rules.append("  {x in %(name)s_%(set)s}:" % self.dict)
        rules.append("  (sum {w in weeks} %(name)s[x,w])" % self.dict)
        rules.append("    <= %(name)s_max[x];" % self.dict)
        return rules

    def get_rule_rest(self):
        rules = []
        rules.append("subject to rest_%(name)s" % self.dict)
        rules.append("  {x in %(name)s_%(set)s, w1 in weeks}:" % self.dict)
        rules.append("  (sum {w2 in w1..(w1 + %(name)s_rest[x]+%(succesive_count)i-1): w2 in weeks} %(name)s[x,w2])" % self.dict)
        rules.append("  <= %(succesive_count)i;" % self.dict)
        return rules

    def get_rule_rest_history(self):
        rules = []
        rules.append("subject to rest_history_%(name)s" % self.dict)
        rules.append("  {x in %(name)s_%(set)s, w in (%(name)s_last[x]+1)..(%(name)s_last[x]+%(name)s_rest[x]): w in weeks}:" % self.dict)
        rules.append("  %(name)s[x,w] == 0;" % self.dict)
        return rules
        
    def get_rule_prefered_pair(self):
        rules = []
        rules.append("subject to prefered_pair_%(name)s" % self.dict)
        rules.append("  {w in weeks, p1 in %(paired_task)s_persons, p2 in %(name)s_persons}:" % self.dict)
        rules.append("  %(paired_task)s[p1,w] + %(name)s[p2,w] <= 1 + %(name)s_prefered_pair[p1,p2] + %(name)s_not_prefered_pair[w];" % self.dict)
        return rules

    def get_rule_missing(self):
        rules = []
        rules.append("subject to missing_%(name)s" % self.dict)
        rules.append("  {w in weeks, t in %(name)s_teams, p in %(name)s_persons: %(name)s_member[t,p]=1 and %(name)s_essential[p]>=1}:" % self.dict)
        rules.append("  %(name)s[t,w] <= %(name)s_available[p,w] + %(name)s_missing[p,w];" % self.dict)
        return rules
		
    def get_rule_maximum_missing(self):
        rules = []
        rules.append("subject to maximum_missing_%(name)s" % self.dict)
        rules.append("  {w in weeks, t in %(name)s_teams}:" % self.dict)
        rules.append("  (sum {p in %(name)s_persons: %(name)s_member[t,p]=1}" % self.dict)
        rules.append("  %(name)s_missing[p,w] * %(name)s_essential[p]) <= %(name)s_maximum_missing[t];" % self.dict)
        return rules

    def get_rule_twice(self):
        rules = []
        rules.append("subject to twice_%(name)s" % self.dict)
        rules.append("  {x in %(name)s_%(set)s, w in 0..(number_of_weeks/2-1): (first_week+2*w+1) in weeks}:" % self.dict)
        rules.append("  %(name)s[x,first_week+2*w] = %(name)s[x,first_week+2*w+1];" % self.dict)
        return rules

    def get_display_lines(self):
        lines = []
        lines.append("display {w in weeks, %(name)s_ in %(name)s_%(set)s: %(name)s[%(name)s_,w]=1}: w, %(name)s_;" % self.dict)
        lines.append("display {w in weeks, rather_not_ in %(name)s_persons: %(name)s_rather_not[rather_not_,w]=1}: w, rather_not_;" % self.dict)
        if self.in_teams:
            lines.append("display {w in weeks, missing_ in %(name)s_persons: %(name)s_missing[missing_,w]=1}: w, missing_;" % self.dict)
        if self.paired_task != None:
            lines.append("display {w in weeks, not_prefered_pair_ in %(name)s_persons: %(name)s_not_prefered_pair[w]=1 and %(name)s[not_prefered_pair_,w]=1}: w, not_prefered_pair_;" % self.dict)
        return lines
    
def read_from(filename, start):
    lines = []
    copy = False
    for line in open(filename, "r"):
        line = line.strip()
        if len(line) == 0:
            copy = False
        if line.startswith(start):
            copy = True
        if copy:
            lines.append(line)
    return lines
    
if __name__ == "__main__":
                    
    tasks = []
    tasks.append(Task("Zangleiding"))
    tasks.append(Task("Muziek",True))
    tasks.append(Task("Geluid"))
    tasks.append(Task("Beamer"))
    tasks.append(Task("Leiding Rood"))
    tasks.append(Task("Groep Rood",paired_task="Leiding Rood"))
    tasks.append(Task("Leiding Wit"))
    tasks.append(Task("Groep Wit",paired_task="Leiding Wit"))
    tasks.append(Task("Leiding Blauw"))
    tasks.append(Task("Groep Blauw",paired_task="Leiding Blauw"))
    tasks.append(Task("Koffie",True))
    tasks.append(Task("Welkom"))
    tasks.append(Task("Hoofdkoster",succesive_count=1))
    tasks.append(Task("Hulpkoster"))

    output = []
    for task in tasks:
        output.extend(task.get_sets())
    output.append("param first_week, integer, >= 1;")
    output.append("param last_week, integer, <= 53;")
    output.append("param number_of_weeks := last_week - first_week+1;")
    output.append("set weeks := first_week .. last_week;")
    output.append("set weeks_extended := (first_week-number_of_weeks+2) .. (last_week+number_of_weeks-2);")
    for task in tasks:
        output.extend(task.get_params())
    for task in tasks:
        output.extend(task.get_vars())
    output.extend(read_from("specials.mod", "var"))
    output.append("minimize penalties:")
    for task in tasks:
        output.extend(task.get_objective_terms())
    output.extend(read_from("specials.mod", "+"))
    output.append(";")
    for task in tasks:
        output.extend(task.get_rules())
    dont_exclude = [("Beamer", "Hulpkoster"), ("Beamer", "Ministry"), ("Groep_Blauw", "Welkom"), 
                    ("Hulpkoster", "Welkom"), ("Leiding_Blauw", "Welkom"), ("Muziek", "Zangleiding")]
                    # ("Ministry", "Welkom"), 
    for task1, task2 in combinations(tasks, 2):
        if not ((task1.name, task2.name) in dont_exclude or (task2.name, task1.name) in dont_exclude):
            output.extend(task1.get_exclusion_rules(task2))
    output.extend(read_from("specials.mod", "subject to"))
    output.append("solve;")
    for task in tasks:
        output.extend(task.get_display_lines())
    output.append("end;")

    for line in output:
        print line
