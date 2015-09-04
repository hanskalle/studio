set assistenten;
set maos;
set stagiares;
set extras;
set medewerkers := assistenten union maos union stagiares union extras;
set taken;
set voorkeurstaken_mao;
set dagen;
set dagdelen;
set fases;
set even_weken;
set oneven_weken;

param eerste_week, integer, >= 1;
param laatste_week, integer, <= 53;
param aantal_weken := laatste_week - eerste_week + 1;
set weken := eerste_week .. laatste_week;

param verlof {m in medewerkers, w in weken, d in dagen}, binary, default 0;
param aanwezigheid {m in medewerkers, d in dagen, l in dagdelen}, binary, default 1;
param competentie {m in medewerkers, t in taken}, binary, default 0;
param bezetting {d in dagen, l in dagdelen, t in taken, f in fases}, integer, >=0, default 1;

var toedeling {w in weken, d in dagen, l in dagdelen, f in fases, t in taken, m in medewerkers}, binary;

maximize voorkeuren:
# Mensen inzetten op de shifts waarvoor ze de voorkeur hebben
#  + (sum {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers}
#    toedeling[w,d,l,f,t,m] * voorkeur[m,d])
# Liever maos in voorkeurstaken voor mao's
  + (sum {w in weken, d in dagen, l in dagdelen, f in fases, t in voorkeurstaken_mao, m in maos}
    toedeling[w,d,l,f,t,m])
# Liever Jeanette niet op tellen
  - 2 * (sum {w in weken, d in dagen, l in dagdelen, f in fases}
    (toedeling[w,d,l,f,'tellenbalie','jeanette'] + toedeling[w,d,l,f,'tellencbbc','jeanette']))
# Zo min mogelijk extras inzetten
  - 10 * (sum {w in weken, d in dagen, l in dagdelen, f in fases, t in taken, m in extras}
    toedeling[w,d,l,f,t,m])
;

subject to partimedag_petra {w in weken: w in oneven_weken}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'do',l,f,t,'petra']) = 0;

subject to partimedag_marylon {w in weken: w in even_weken}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'do',l,f,t,'marylon']) = 0;

subject to partimedag_firdous {w in weken: w in oneven_weken}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'vr',l,f,t,'firdous']) = 0;

subject to bezetting_per_taak {w in weken, d in dagen, l in dagdelen, f in fases, t in taken}:
    (sum {m in medewerkers} toedeling[w,d,l,f,t,m]) = bezetting[d,l,t,f];

subject to maximaal_1_taak_per_medewerker_per_dagdeel_en_fase
    {w in weken, d in dagen, l in dagdelen, f in fases, m in medewerkers}:
    (sum {t in taken} toedeling[w,d,l,f,t,m]) <= 1;

subject to niet_toedelen_wanneer_niet_aanwezig {m in medewerkers, d in dagen, l in dagdelen: aanwezigheid[m,d,l]=0}:
    (sum {w in weken, f in fases, t in taken} toedeling[w,d,l,f,t,m]) = 0;
    
subject to niet_toedelen_op_wanneer_verlof {m in medewerkers, w in weken, d in dagen: verlof[m,w,d]=1}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,d,l,f,t,m]) = 0;
    
subject to niet_toedelen_als_competentie_ontbreekt {m in medewerkers, t in taken: competentie[m,t]=0}:
    (sum {w in weken, d in dagen, l in dagdelen, f in fases} toedeling[w,d,l,f,t,m]) = 0;
    
subject to niet_voor_en_namiddag_dezelfde_taak {w in weken, d in dagen, f in fases, t in taken, m in medewerkers}:
    (sum {l in dagdelen} toedeling[w,d,l,f,t,m]) <= 1;
    
subject to fokkelien_niet_starten_met_baxter {w in weken, d in dagen, l in dagdelen}:
    toedeling[w,d,l,'start','baxter','fokkelien'] = 0;
    
subject to jeanette_niet_tellen_op_vrijdag {w in weken, d in dagen, l in dagdelen, f in fases}:
    toedeling[w,d,l,f,'tellenbalie','jeanette'] + toedeling[w,d,l,f,'tellencbbc','jeanette'] = 0;

subject to een_gestarte_taak_wordt_dezelfde_medewerker_uitgevoerd
    {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers: bezetting[d,l,t,'start'] <= bezetting[d,l,t,'daarna']}:
    toedeling[w,d,l,'start',t,m] <= toedeling[w,d,l,'daarna',t,m];

solve;

display toedeling;

end;
