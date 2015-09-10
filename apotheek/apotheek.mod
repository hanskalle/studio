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
set shifts;

param eerste_week, integer, >= 1;
param laatste_week, integer, <= 53;
param aantal_weken := laatste_week - eerste_week + 1;
set weken := eerste_week .. laatste_week;

param verlof {m in medewerkers, w in weken, d in dagen}, binary, default 0;
param aanwezigheid {m in medewerkers, d in dagen, l in dagdelen}, binary, default 1;
param competentie {m in medewerkers, t in taken}, binary, default 0;
param minimale_inzet {m in medewerkers, t in taken}, default 0;
param bezetting {d in dagen, l in dagdelen, t in taken, f in fases}, integer, >=0, default 1;
param aantal_per_shift {d in dagen, s in shifts}, integer, >=0, default 0;
param shiftvoorkeur {m in medewerkers, d in dagen, s in shifts}, binary, default 0;

var toedeling {w in weken, d in dagen, l in dagdelen, f in fases, t in taken, m in medewerkers}, binary;
var shift {w in weken, d in dagen, s in shifts, m in medewerkers}, binary;

maximize voorkeuren:
# Zoveel mogelijk toedelen
  + (sum {w in weken, d in dagen, l in dagdelen, f in fases, t in taken, m in medewerkers}
    toedeling[w,d,l,f,t,m])
# Mensen inzetten op de shifts waarvoor ze de voorkeur hebben
  + 5 * (sum {w in weken, d in dagen, m in medewerkers, s in shifts}
    shift[w,d,s,m] * shiftvoorkeur[m,d,s])
# Liever maos in voorkeurstaken voor mao's
  + 2 * (sum {w in weken, d in dagen, l in dagdelen, f in fases, t in voorkeurstaken_mao, m in maos}
    toedeling[w,d,l,f,t,m])
# Liever Jeanette niet op tellen
  - 2 * (sum {w in weken, d in dagen, l in dagdelen, f in fases}
    (toedeling[w,d,l,f,'tellenbalie','jeanette'] + toedeling[w,d,l,f,'tellencbbc','jeanette']))
# Zo min mogelijk onbezet laten
  - 10 * (sum {w in weken, d in dagen, l in dagdelen, f in fases, t in taken, m in extras}
    toedeling[w,d,l,f,t,m])
;


# Bezetting
subject to bezetting_per_taak {w in weken, d in dagen, l in dagdelen, f in fases, t in taken: t != 'extra'}:
    (sum {m in medewerkers} toedeling[w,d,l,f,t,m]) = bezetting[d,l,t,f];

subject to maximaal_1_taak_per_medewerker_per_dagdeel_en_fase
    {w in weken, d in dagen, l in dagdelen, f in fases, m in medewerkers}:
    (sum {t in taken} toedeling[w,d,l,f,t,m]) <= 1;


# Aanwezigheid
subject to niet_toedelen_wanneer_niet_aanwezig {m in medewerkers, d in dagen, l in dagdelen: aanwezigheid[m,d,l]=0}:
    (sum {w in weken, f in fases, t in taken} toedeling[w,d,l,f,t,m]) = 0;
    
subject to niet_toedelen_op_wanneer_verlof {m in medewerkers, w in weken, d in dagen: verlof[m,w,d]=1}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,d,l,f,t,m]) = 0;
    
subject to partimedag_petra {w in weken: w in oneven_weken}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'do',l,f,t,'petra']) = 0;

subject to partimedag_marylon {w in weken: w in even_weken}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'do',l,f,t,'marylon']) = 0;

subject to partimedag_firdous {w in weken: w in oneven_weken}:
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'vr',l,f,t,'firdous']) = 0;


# Competenties en het actief houden daarvan
subject to minimale_inzet_bewaken
    {m in medewerkers, t in taken}:
    (sum {w in weken, d in dagen, l in dagdelen, f in fases} toedeling[w,d,l,f,t,m]) >= minimale_inzet[m,t]*aantal_weken/2;

subject to niet_toedelen_als_competentie_ontbreekt {m in medewerkers, t in taken: competentie[m,t]=0}:
    (sum {w in weken, d in dagen, l in dagdelen, f in fases} toedeling[w,d,l,f,t,m]) = 0;


# Afspraken werkverdeling    
subject to niet_voor_en_namiddag_dezelfde_taak {w in weken, d in dagen, f in fases, t in taken, m in medewerkers}:
    (sum {l in dagdelen} toedeling[w,d,l,f,t,m]) <= 1;

subject to een_gestarte_taak_wordt_dezelfde_medewerker_ook_daarna_gedaan
    {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers: bezetting[d,l,t,'start'] <= bezetting[d,l,t,'daarna']}:
    toedeling[w,d,l,'start',t,m] <= toedeling[w,d,l,'daarna',t,m];


# Shifts    
subject to aantal_in_vroege_en_late_shifts {w in weken, d in dagen, s in shifts: s!='standaard'}:
    (sum {m in medewerkers} shift[w,d,s,m]) = aantal_per_shift[d,s];
    
subject to medewerker_hoogstens_in_1_shift {w in weken, d in dagen, m in medewerkers}:
    (sum {s in shifts} shift[w,d,s,m]) <= 1;

subject to medewerker_alleen_in_shift_als_aanwezig {w in weken, d in dagen, m in medewerkers: (sum {l in dagdelen} aanwezigheid[m,d,l])=0}:
    (sum {s in shifts} shift[w,d,s,m]) = 0;

subject to als_toegedeeld_dan_ook_shift {w in weken, d in dagen, m in medewerkers: (sum {l in dagdelen} aanwezigheid[m,d,l])>0}:
    (sum {s in shifts} shift[w,d,s,m]) = 1;

#subject to extras_alleen_standaard_shift {w in weken, d in dagen, m in extras}:
#    (sum {s in shifts: s!='standaard'} shift[w,d,s,m]) = 0;
    
subject to vroege_shifts_starten_op_balie {w in weken, d in dagen, m in medewerkers}:
    shift[w,d,'vroeg',m] <= toedeling[w,d,'vm','start','balie',m];

subject to late_shifts_eindigen_op_balie  {w in weken, d in dagen, m in medewerkers}:
    shift[w,d,'laat',m] <= toedeling[w,d,'nm','daarna','balie',m];


# Speciale regels
subject to fokkelien_niet_starten_met_baxter {w in weken, d in dagen, l in dagdelen}:
    toedeling[w,d,l,'start','baxter','fokkelien'] = 0;
    
subject to jeanette_niet_tellen_op_vrijdag {w in weken, d in dagen, l in dagdelen, f in fases}:
    toedeling[w,d,l,f,'tellenbalie','jeanette'] + toedeling[w,d,l,f,'tellencbbc','jeanette'] = 0;

solve;

display toedeling;
display shift;

end;
