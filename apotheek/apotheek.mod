set assistenten;
set maos;
set stagiares;
set medewerkers := assistenten union maos union stagiares;
set taken;
set voorkeurstaken_mao;
set dagen;
set dagdelen;

param eerste_week, integer, >= 1;
param laatste_week, integer, <= 53;
param aantal_weken := laatste_week - eerste_week + 1;
set weken := eerste_week .. laatste_week;

param beschikbaar {m in medewerkers, w in weken, d in dagen}, binary, default 1;
param werktijd {m in medewerkers, d in dagen, l in dagdelen}, binary, default 1;
param voorkeur {m in medewerkers, d in dagen}, binary;

var toedeling {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers}, binary;

maximize voorkeuren:
  + (sum {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers}
    toedeling[w,d,l,t,m] * voorkeur[m,d])
  + (sum {w in weken, d in dagen, l in dagdelen, t in voorkeurstaken_mao, m in maos}
    toedeling[w,d,l,t,m])
  - (sum {w in weken, d in dagen, l in dagdelen}
    toedeling[w,d,l,'tellen','jeanette'])
;

subject to een_per_taak {w in weken, d in dagen, l in dagdelen, t in taken}:
    (sum {m in medewerkers} toedeling[w,d,l,t,m]) = 1;

subject to maar_een_taak_per_medewerker_per_dag {w in weken, d in dagen, l in dagdelen, m in medewerkers}:
    (sum {t in taken} toedeling[w,d,l,t,m]) <= 1;

subject to niet_toedelen_op_niet_werktijden {m in medewerkers, d in dagen, l in dagdelen: werktijd[m,d,l]=0}:
    (sum {w in weken, t in taken} toedeling[w,d,l,t,m]) = 0;
    
subject to jeanette_niet_tellen_op_vrijdag {w in weken, d in dagen, l in dagdelen}:
    toedeling[w,d,l,'tellen','jeanette'] = 0;

solve;

display toedeling;

end;
