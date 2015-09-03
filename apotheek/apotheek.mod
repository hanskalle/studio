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
param competentie {m in medewerkers, t in taken}, binary, default 0;
param bezetting {d in dagen, l in dagdelen, t in taken}, integer, >=0, default 1;

var toedeling {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers}, binary;

maximize voorkeuren:
  + (sum {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers}
    toedeling[w,d,l,t,m] * voorkeur[m,d])
  + (sum {w in weken, d in dagen, l in dagdelen, t in voorkeurstaken_mao, m in maos}
    toedeling[w,d,l,t,m])
  - (sum {w in weken, d in dagen, l in dagdelen}
    toedeling[w,d,l,'tellen','jeanette'])
;

subject to bezetting_per_taak {w in weken, d in dagen, l in dagdelen, t in taken}:
    (sum {m in medewerkers} toedeling[w,d,l,t,m]) = bezetting[d,l,t];

subject to maar_een_taak_per_medewerker_per_dagdeel {w in weken, d in dagen, l in dagdelen, m in medewerkers}:
    (sum {t in taken} toedeling[w,d,l,t,m]) <= 1;

subject to niet_toedelen_op_niet_werktijden {m in medewerkers, d in dagen, l in dagdelen: werktijd[m,d,l]=0}:
    (sum {w in weken, t in taken} toedeling[w,d,l,t,m]) = 0;
    
subject to niet_toedelen_als_competentie_ontbreekt {m in medewerkers, t in taken: competentie[m,t]=0}:
    (sum {w in weken, d in dagen, l in dagdelen} toedeling[w,d,l,t,m]) = 0;
    
subject to niet_voor_en_namiddag_dezelfde_taak {w in weken, d in dagen, t in taken, m in medewerkers}:
    (sum {l in dagdelen} toedeling[w,d,l,t,m]) <= 1;
    
subject to fokkelien_niet_baxter_in_haar_eentje {d in dagen, l in dagdelen: bezetting[d,l,'baxter']<2}:
    (sum {w in weken} toedeling[w,d,l,'baxter','fokkelien']) = 0;
    
subject to jeanette_niet_tellen_op_vrijdag {w in weken, d in dagen, l in dagdelen}:
    toedeling[w,d,l,'tellen','jeanette'] = 0;

solve;

display toedeling;

end;
