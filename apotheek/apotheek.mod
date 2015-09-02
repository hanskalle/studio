set medewerkers;

set taken;

param ma := 0;
param di := 1;
param wo := 2;
param do := 3;
param vr := 4;
set dagen := ma..vr;

param eerste_week, integer, >= 1;
param laatste_week, integer, <= 53;
param aantal_weken := laatste_week - eerste_week + 1;
set weken := eerste_week .. laatste_week;

param beschikbaar {m in medewerkers, w in weken, d in dagen}, binary;
param werkdag {m in medewerkers, d in dagen}, binary;
param voorkeur {m in medewerkers, d in dagen}, binary;


var toedeling {w in weken, d in dagen, t in taken, m in medewerkers}, binary;

maximize voorkeuren:
  + (sum {w in weken, d in dagen, t in taken, m in medewerkers}
    toedeling[w,d,t,m] * voorkeur[m,d]);

subject to een_per_taak {w in weken, d in dagen, t in taken}:
    (sum {m in medewerkers} toedeling[w,d,t,m]) = 1;

subject to ma_een_taak_per_medewerker_per_dag {w in weken, d in dagen, m in medewerkers}:
    (sum {t in taken} toedeling[w,d,t,m]) <= 1;

subject to niet_toedelen_op_niet_werkdagen {m in medewerkers, d in dagen: werkdag[m,d]=0}:
    (sum {w in weken, t in taken} toedeling[w,d,t,m]) = 0;

solve;

display {w in weken, d in dagen, t in taken, m in medewerkers: toedeling[w,d,t,m]=1}: w, d, t, m;

end;
