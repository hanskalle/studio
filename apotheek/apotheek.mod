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
var taakbreuk {w in weken, d in dagen, l in dagdelen, m in medewerkers}, binary;
var taakbreukbalie {w in weken, d in dagen, l in dagdelen, m in medewerkers}, binary;
var niet_vroege_woensdagbaxter {w in weken, m in medewerkers}, binary;

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
    (toedeling[w,d,l,f,'tellenbalie','jeanette'] + toedeling[w,d,l,f,'tellencbbct','jeanette']))
# Zo min mogelijk onbezet laten, maar als het dan moet, dan maar balie
  - 40 * (sum {w in weken, d in dagen, l in dagdelen, f in fases, t in taken, m in extras: t!='balie'}
    toedeling[w,d,l,f,t,m])
  - 20 * (sum {w in weken, d in dagen, l in dagdelen, f in fases, m in extras}
    toedeling[w,d,l,f,'balie',m])
# Zo min mogelijk taakbreuken
  - 1 * (sum {w in weken, d in dagen, l in dagdelen, m in medewerkers}
    taakbreuk[w,d,l,m])
# En nog minder taakbreuken bij balie
  - 5 * (sum {w in weken, d in dagen, l in dagdelen, m in medewerkers}
    taakbreukbalie[w,d,l,m])
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
    (sum {l in dagdelen, f in fases, t in taken} toedeling[w,'do',l,f,t,'firdous']) = 0;


# Competenties en het actief houden daarvan
subject to minimale_inzet_bewaken
    {m in medewerkers, t in taken}:
    (sum {w in weken, d in dagen, l in dagdelen, f in fases} toedeling[w,d,l,f,t,m]) >= (minimale_inzet[m,t] * aantal_weken) div 2;

subject to niet_toedelen_als_competentie_ontbreekt {m in medewerkers, t in taken: competentie[m,t]=0}:
    (sum {w in weken, d in dagen, l in dagdelen, f in fases} toedeling[w,d,l,f,t,m]) = 0;


# Afspraken werkverdeling    
subject to niet_voor_en_namiddag_dezelfde_taak {w in weken, d in dagen, f in fases, t in taken, m in medewerkers}:
    (sum {l in dagdelen} toedeling[w,d,l,f,t,m]) <= 1;

subject to een_gestarte_taak_wordt_het_liefst_door_dezelfde_medewerker_ook_daarna_gedaan
    {w in weken, d in dagen, l in dagdelen, t in taken, m in medewerkers}:
    toedeling[w,d,l,'start',t,m] <= toedeling[w,d,l,'daarna',t,m] + taakbreuk[w,d,l,m];

subject to starten_op_de_balie_wordt_daarna_ook_gedaan
    {w in weken, d in dagen, l in dagdelen, m in medewerkers: (m not in extras) and (bezetting[d,l,'balie','start'] <= bezetting[d,l,'balie','daarna'])}:
    toedeling[w,d,l,'start','balie',m] <= toedeling[w,d,l,'daarna','balie',m] + taakbreukbalie[w,d,l,m];

subject to tellencbbct_vm_start_met_bestelling {w in weken, d in dagen, m in medewerkers: bezetting[d,'vm','tellencbbct','start'] < bezetting[d,'vm','tellencbbct','daarna']}:
    toedeling[w,d,'vm','daarna','tellencbbct',m] <= toedeling[w,d,'vm','start','bestelling',m];

subject to typenhh_vm_start_met_bestelling {w in weken, d in dagen, m in medewerkers: bezetting[d,'vm','typenhh','start'] < bezetting[d,'vm','typenhh','daarna']}:
    toedeling[w,d,'vm','daarna','typenhh',m] <= toedeling[w,d,'vm','start','bestelling',m];
    
subject to na_typencito_geen_tellenbalie1 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typencito',m] + toedeling[w,d,'vm','daarna','tellenbalie',m] <= 1;

subject to na_typencito_geen_tellenbalie2 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typencito',m] + toedeling[w,d,'nm','start','tellenbalie',m] <= 1;

subject to na_typencito_geen_tellenbalie3 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typencito',m] + toedeling[w,d,'nm','daarna','tellenbalie',m] <= 1;

subject to na_typencito_geen_tellenbalie4 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','daarna','typencito',m] + toedeling[w,d,'nm','start','tellenbalie',m] <= 1;

subject to na_typencito_geen_tellenbalie5 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','daarna','typencito',m] + toedeling[w,d,'nm','daarna','tellenbalie',m] <= 1;

subject to na_typencito_geen_tellenbalie6 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'nm','start','typencito',m] + toedeling[w,d,'nm','daarna','tellenbalie',m] <= 1;
    
subject to na_typenhh_geen_tellenbalie1 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typenhh',m] + toedeling[w,d,'vm','daarna','tellenbalie',m] <= 1;

subject to na_typenhh_geen_tellenbalie2 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typenhh',m] + toedeling[w,d,'nm','start','tellenbalie',m] <= 1;

subject to na_typenhh_geen_tellenbalie3 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typenhh',m] + toedeling[w,d,'nm','daarna','tellenbalie',m] <= 1;

subject to na_typenhh_geen_tellenbalie4 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','daarna','typenhh',m] + toedeling[w,d,'nm','start','tellenbalie',m] <= 1;

subject to na_typenhh_geen_tellenbalie5 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','daarna','typenhh',m] + toedeling[w,d,'nm','daarna','tellenbalie',m] <= 1;

subject to na_typenhh_geen_tellenbalie6 {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'nm','start','typenhh',m] + toedeling[w,d,'nm','daarna','tellenbalie',m] <= 1;


# Shifts    
subject to aantal_in_vroege_en_late_shifts {w in weken, d in dagen, s in shifts: s!='standaard'}:
    (sum {m in medewerkers} shift[w,d,s,m]) = aantal_per_shift[d,s];
    
subject to medewerker_hoogstens_in_1_shift {w in weken, d in dagen, m in medewerkers}:
    (sum {s in shifts} shift[w,d,s,m]) <= 1;

subject to medewerker_alleen_in_shift_als_aanwezig {w in weken, d in dagen, m in medewerkers: (sum {l in dagdelen} aanwezigheid[m,d,l])=0}:
    (sum {s in shifts} shift[w,d,s,m]) = 0;

subject to als_toegedeeld_dan_ook_shift {w in weken, d in dagen, m in medewerkers: (sum {l in dagdelen} aanwezigheid[m,d,l])>0}:
    (sum {s in shifts} shift[w,d,s,m]) = 1;

subject to minimaal_twee_assisten_in_vroege_shift {w in weken, d in dagen}:
    (sum {m in assistenten} shift[w,d,'vroeg',m]) >= 2;

subject to minimaal_twee_assisten_in_late_shift {w in weken, d in dagen}:
    (sum {m in assistenten} shift[w,d,'laat',m]) >= 2;

subject to als_starten_met_bestelling_dan_vroeg_beginnen {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','bestelling',m] <= shift[w,d,'vroeg',m];

subject to noteer_baxters_die_op_woensdag_niet_vroeg_beginnen {w in weken, m in medewerkers}:
    toedeling[w,'wo','vm','start','baxter',m] <= shift[w,'wo','vroeg',m] + niet_vroege_woensdagbaxter[w,m];

subject to minstens_1_vroege_baxters_op_woensdag {w in weken}:
    (sum {m in medewerkers} niet_vroege_woensdagbaxter[w,m]) + 1 = bezetting['wo','vm','baxter','start'];

subject to als_starten_met_typencito_dan_geen_late_shift {w in weken, d in dagen, m in medewerkers}:
    toedeling[w,d,'vm','start','typencito',m] <= 1 - shift[w,d,'laat',m];


# Vaste taken
subject to martine_op_di_vm_even_weken_extra_taak {w in weken, f in fases: w in even_weken}:
    toedeling[w,'di','vm',f,'extra','martine'] >= 1 - verlof['martine',w,'di'];

subject to silvia_eens_per_4_weken_in_oneven_week_op_do_extra_taak {w in weken, f in fases: (w+1) mod 4 = 0}:
    toedeling[w,'do','vm',f,'extra','silvia'] >= 1 - verlof['silvia',w,'do'];

subject to kirsten_eens_per_4_weken_in_oneven_week_op_do_extra_taak {w in weken, f in fases: (w+3) mod 4 = 0}:
    toedeling[w,'do','vm',f,'extra','kirsten'] >= 1 - verlof['kirsten',w,'do'];


# Speciale regels
subject to fokkelien_niet_starten_met_baxter {w in weken, d in dagen, l in dagdelen}:
    toedeling[w,d,l,'start','baxter','fokkelien'] = 0;
    
subject to jeanette_niet_tellen_op_vrijdag {w in weken, d in dagen, l in dagdelen, f in fases}:
    toedeling[w,d,l,f,'tellenbalie','jeanette'] + toedeling[w,d,l,f,'tellencbbct','jeanette'] = 0;


solve;

display toedeling;
display shift;

end;
