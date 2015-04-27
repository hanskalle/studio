#!/usr/bin/env python

def createSetnames(single_tasks, team_tasks, pair_tasks):
    setnames = []
    for task in single_tasks:
        setnames.append("set %s_persons;" % task)
    for task in team_tasks:
        setnames.append("set %s_persons;" % task)
        setnames.append("set %s_teams;" % task)
    for task, pair in pair_tasks:
        setnames.append("set %s_persons;" % task)
        if task != pair:
            setnames.append("set %s_persons;" % pair)
    return setnames
    
def createParams(task,isTeam=False,pair=None):
    params = []
    params.append("param %s_offritme_penalty, >=0;" % task)
    params.append("param %s_rather_not_penalty, >=0;" % task)
    if isTeam:
        setname = "teams"
        params.append("param %s_member {t in %s_teams, p in %s_persons}, binary;" % (task, task, task))
        params.append("param %s_maximum_missing {t in %s_teams}, >= 0;" % (task, task))
        params.append("param %s_essential {p in %s_persons}, >= 0;" % (task, task))
    else:
        setname = "persons"
    params.append("param %s_available {p in %s_persons, w in weeks}, >=0, <=1;" % (task, task))
    params.append("param %s_ritme {x in %s_%s}, integer, >=1;" % (task, task, setname))
    params.append("param %s_rest {x in %s_%s}, integer, >=0;" % (task, task, setname))
    if pair != None:
        params.append("param %s_prefered_pair {p1 in %s_persons, p2 in %s_persons}, binary;" % (pair, task, pair))
        params.append("param %s_not_prefered_pair_penalty, >=0;" % pair)
        if pair != task:
            params.append("param %s_rather_not_penalty, >=0;" % pair)
            params.append("param %s_available {p in %s_persons, w in weeks}, >=0, <=1;" % (pair, pair))
    return params
    
def createVariables(task,isTeam=False,pair=None):
    variables = []
    if isTeam:
        setname = "teams"
        variables.append("var %s_missing {p in %s_persons, w in weeks}, binary;" % (task, task))
    else:
        setname = "persons"
    variables.append("var %s {x in %s_%s, w in weeks}, binary;" % (task, task, setname))
    variables.append("var %s_offritme {x in %s_%s, w in weeks_extended}, binary;" % (task, task, setname))
    variables.append("var %s_rather_not {p in %s_persons, w in weeks}, binary;" % (task, task))
    if pair != None:
        variables.append("var %s_not_prefered_pair {w in weeks}, binary;" % pair)
        if pair != task:
            variables.append("var %s {p in %s_persons, w in weeks}, binary;" % (pair, pair))
            variables.append("var %s_rather_not {p in %s_persons, w in weeks}, binary;" % (pair, pair))
    return variables
    
def createRules(task,isTeam=False,pair=None):
    rules = []
    if isTeam:
        setname = "teams"
        addRuleAvailableTeam(rules,task)
        addRuleMissing(rules,task)
        addRuleMaximumMissing(rules,task)
    else:
        setname = "persons"
        addRuleAvailablePersons(rules,task)
    addRuleSingle(rules,task,setname)
    addRuleRitme(rules,task,setname)
    addRuleMinimum(rules,task,setname)
    addRuleMaximum(rules,task,setname)
    addRuleRest(rules,task,setname)
    if pair != None:
        addRuleSinglePair(rules,pair)
        addRuleAvailablePair(rules,pair)
        addRulePreferedPair(rules,task,pair)
        if task == pair:
            addRuleExclusion(rules,task,pair)
    return rules
    
def addRuleSingle(rules,task,setname):
    rules.append("subject to single_%s" % task)
    rules.append("  {w in weeks}:")
    rules.append("  (sum {x in %s_%s} %s[x,w]) = 1;" % (task, setname, task))

def addRuleAvailablePersons(rules,task):
    rules.append("subject to available_%s" % task)
    rules.append("  {w in weeks, p in %s_persons}:" % task)
    rules.append("  %s[p,w] <= %s_available[p,w] + 0.5 * %s_rather_not[p,w];" % (task, task, task))

def addRuleAvailableTeam(rules,task):
    rules.append("subject to available_%s" % task)
    rules.append("  {w in weeks, t in %s_teams, p in %s_persons: %s_member[t,p]=1 and %s_essential[p]=0}:" % (task, task, task, task))
    rules.append("  %s[t,w] <= %s_available[p,w] + 0.5 * %s_rather_not[p,w];" % (task, task, task))

def addRuleRitme(rules,task,setname):
    rules.append("subject to ritme_%s" % task)
    rules.append("  {w1 in weeks_extended, x in %s_%s}:" % (task,setname))
    rules.append("  (sum {w2 in w1..(w1 + %s_ritme[x]-1): w2 in weeks} %s[x,w2])" % (task, task))
    rules.append("    <= 1 + %s_offritme[x,w1];" % task)

def addRuleMinimum(rules,task,setname):
    rules.append("subject to minimum_%s" % task)
    rules.append("  {x in %s_%s}:" % (task, setname))
    rules.append("  (sum {w in weeks} %s[x,w])" % task)
    rules.append("    >= number_of_weeks/%s_ritme[x]-2;" % task)

def addRuleMaximum(rules,task,setname):
    rules.append("subject to maximum_%s" % task)
    rules.append("  {x in %s_%s}:" % (task, setname))
    rules.append("  (sum {w in weeks} %s[x,w])" % task)
    rules.append("    <= number_of_weeks/%s_ritme[x]+2;" % task)

def addRuleRest(rules,task,setname):
    rules.append("subject to rest_%s" % task)
    rules.append("  {x in %s_%s, w1 in weeks}:" % (task, setname))
    rules.append("  (sum {w2 in w1..(w1 + %s_rest[x]): w2 in weeks} %s[x,w2])" % (task, task))
    rules.append("    <= 1;")

def addRuleMissing(rules,task):
    rules.append("subject to missing_%s" % task)
    rules.append("  {w in weeks, t in %s_teams, p in %s_persons: %s_member[t,p]=1 and %s_essential[p]>=1}:" % (task, task, task, task))
    rules.append("  %s[t,w] <= %s_available[p,w] + %s_missing[p,w];" % (task, task, task))
		
def addRuleMaximumMissing(rules,task):
    rules.append("subject to maximum_missing_%s" % task)
    rules.append("  {w in weeks, t in %s_teams}:" % task)
    rules.append("  (sum {p in %s_persons: %s_member[t,p]=1} %s_missing[p,w] * %s_essential[p]) <= %s_maximum_missing[t];" % (task, task, task, task, task))
    
def addRuleSinglePair(rules,pair):
    rules.append("subject to single_%s" % pair)
    rules.append("  {w in weeks}:")
    rules.append("	(sum {p in %s_persons} %s[p,w]) = 1;" % (pair, pair))

def addRuleAvailablePair(rules,pair):
    rules.append("subject to available_%s" % pair)
    rules.append("  {w in weeks, p in %s_persons}:" % pair)
    rules.append("  %s[p,w] <= %s_available[p,w];" % (pair, pair))
                
def addRulePreferedPair(rules,task,pair):
    rules.append("subject to prefered_pair_%s" % pair)
    rules.append("  {w in weeks, p1 in %s_persons, p2 in %s_persons}:" % (task,pair))
    rules.append("  %s[p1,w] + %s[p2,w] <= 1 + %s_prefered_pair[p1,p2] + %s_not_prefered_pair[w];" % (task,pair,pair,pair))
                
def addRuleExclusionPair(rules,task,pair):
    rules.append("subject to exclusion_%s" % pair)
    rules.append("  {w in weeks, p in %s_persons}:" % task)
    rules.append("  %s[p,w] + %s[p,w] <= 1;" % (task,pair))
    
def addRuleExclusion(rules,task,pair):
    rules.append("subject to exclusion_%s" % pair)
    rules.append("  {w in weeks, p in %s_persons}:" % task)
    rules.append("  %s[p,w] + %s[p,w] <= 1;" % (task,pair))

def createExclusionRules(task1,task2):
    rules = []
    rules.append("subject to %s_excludes_%s" % (task1, task2))
    if task1 != "Muziek":
        rules.append("  {w in weeks, p in %s_persons inter %s_persons}:" % (task1, task2))
        rules.append("  %s[p,w] + %s[p,w] <= 1;" % (task1,task2))
    else:
        rules.append("  {w in weeks, p in %s_persons inter %s_persons, t in %s_teams: %s_member[t,p]=1}:" % (task1, task2, task1, task1))
        rules.append("  %s[t,w] + %s[p,w] <= 1;" % (task1,task2))
    return rules
    
def createDisplay(task,isTeam=False,pair=None):
    lines = []
    if isTeam:
        setname = "teams"
        lines.append("display {w in weeks, missing_ in %s_persons: %s_missing[missing_,w]=1}: w, missing_;" % (task, task))
    else:
        setname = "persons"
    lines.append("display {w in weeks, %s_ in %s_%s: %s[%s_,w]=1}: w, %s_;" % (task, task, setname, task, task, task))
    lines.append("display {w in weeks, rather_not_ in %s_persons: %s_rather_not[rather_not_,w]=1}: w, rather_not_;" % (task, task))
    if pair != None:
        lines.append("display {w in weeks, not_prefered_pair_ in %s_persons: %s_not_prefered_pair[w]=1 and %s[not_prefered_pair_,w]=1}: w, not_prefered_pair_;" % (pair, pair, pair))
    return lines
    
def addPenaltyOffritme(objective, task, setname):
    objective.append("  + (sum {x in %s_%s, w in weeks_extended} %s_offritme_penalty * %s_offritme[x,w])" % (task, setname, task, task))
    
def addPenaltyMissing(objective, task):
    objective.append("  + (sum {p in %s_persons, w in weeks} %s_essential[p] * %s_missing[p,w])" % (task, task, task))

def addPenaltyPair(objective, pair):
    objective.append("  + (sum {w in weeks} %s_not_prefered_pair_penalty * %s_not_prefered_pair[w])" % (pair, pair))
    
def addPenaltyRatherNot(objective, task):
    objective.append("  + (sum {p in %s_persons, w in weeks} %s_rather_not_penalty * %s_rather_not[p,w])" % (task, task, task))

def createObjective(single_tasks, team_tasks, pair_tasks):
    objective = ["minimize penalties:"]
    for task in single_tasks:
        addPenaltyOffritme(objective, task, "persons")
        addPenaltyRatherNot(objective, task)
    for task in team_tasks:
        addPenaltyOffritme(objective, task, "teams")
        addPenaltyRatherNot(objective, task)
        addPenaltyMissing(objective, task)
    for task, pair in pair_tasks:
        addPenaltyOffritme(objective, task, "persons")
        if task != pair:
            addPenaltyRatherNot(objective, pair)
        addPenaltyPair(objective, pair)
    objective.append(";")
    return objective
    
if __name__ == "__main__":
    single_tasks = ["Zangleiding", "Geluid", "Beamer", "Leiding_Rood", "Welkom", "Hoofdkoster", "Hulpkoster"]
    team_tasks = ["Muziek", "Koffie"]
    pair_tasks = [("Leiding_Blauw", "Groep_Blauw"), ("Leiding_Wit", "Groep_Wit")] #, ("Ministry", "Ministry")]
    exclusions = [("Zangleiding", "Geluid"), ("Muziek", "Welkom"), ("Zangleiding", "Leiding_Rood"),
                    ("Muziek", "Hulpkoster"), ("Beamer", "Geluid"), ("Muziek", "Beamer"),
                    ("Groep_Blauw", "Beamer"), ("Groep_Wit", "Beamer"), ("Hulpkoster", "Beamer")]
                    
    for setname in createSetnames(single_tasks, team_tasks, pair_tasks):
        print setname
    print "param first_week, integer, >= 1;"
    print "param last_week, integer, <= 53;"
    print "param number_of_weeks := last_week - first_week+1;"
    print "set weeks := first_week .. last_week;"
    print "set weeks_extended := (first_week-number_of_weeks+2) .. (last_week+number_of_weeks-2);"
    for task in single_tasks:
        for param in createParams(task):
            print param
    for task in team_tasks:
        for param in createParams(task,True):
            print param
    for task, pair in pair_tasks:
        for param in createParams(task,False,pair):
            print param
    for task in single_tasks:
        for variable in createVariables(task):
            print variable
    for task in team_tasks:
        for variable in createVariables(task,True):
            print variable
    for task, pair in pair_tasks:
        for variable in createVariables(task,False,pair):
            print variable
    for objectives in createObjective(single_tasks, team_tasks, pair_tasks):
        print objectives
    for task in single_tasks:
        for rule in createRules(task):
            print rule
    for task in team_tasks:
        for rule in createRules(task,True):
            print rule
    for task1, task2 in pair_tasks:
        for rule in createRules(task1,False,task2):
            print rule
    for task1, task2 in exclusions:
        for rule in createExclusionRules(task1, task2):
            print rule
    for line in open('specials.mod'):
        print line[0:-1]
    print "solve;"
    for task in single_tasks:
        for line in createDisplay(task):
            print line
    for task in team_tasks:
        for line in createDisplay(task,True):
            print line
    for task, pair in pair_tasks:
        for line in createDisplay(task,False,pair):
            print line
        if task != pair:
            for line in createDisplay(pair):
                print line
    print "end;"

