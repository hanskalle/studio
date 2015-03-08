# Plannen van het Ichthus-rooster
#

### sets ###

set muzikanten;
set teams within muzikanten;
set leiders;
set dubbelleiders := teams inter leiders;
set schuivers;
set beamers;
set leiders_blauw;
set helpers_blauw;
set blauw := leiders_blauw union helpers_blauw;
set leiders_wit;
set helpers_wit;
set wit := leiders_wit union helpers_wit;
set leiders_rood;
set rood := leiders_rood;
set schenkers;
set koffieteams;
set gastvrouwen;

set personen := muzikanten union leiders union schuivers union beamers union blauw union wit union rood union schenkers union gastvrouwen;

### parameters ###

param eerste_week, integer, >= 1;
param laatste_week, integer, >= eerste_week, <= 53;
set zondagen := eerste_week .. laatste_week;
param beschikbaar {p in personen, z in zondagen}, >=0, <=1;
param teamlid {t in teams, m in muzikanten}, binary;
param teamminimum {t in teams}, >=0;
param teammaximum {t in teams}, >=1;
param teamrustminimum {t in teams}, >=0;
param teamritmegewenst {t in teams}, >=0;
param leiderminimum {t in leiders}, >=0;
param leidermaximum {t in leiders}, >=1;
param leiderrust {t in leiders}, >=0;
param teamlidmisbaar {m in muzikanten}, >=0;
param schuiverritmegewenst {s in schuivers}, >=0;
param beamerritmegewenst {b in beamers}, >=0;
param blauwritmegewenst {l in leiders_blauw}, >=0;
param voorkeurpaar_blauw {l in leiders_blauw, h in helpers_blauw}, binary;
param witritmegewenst {l in leiders_wit}, >=0;
param voorkeurpaar_wit {l in leiders_wit, h in helpers_wit}, binary;
param roodritmegewenst {l in leiders_rood}, >=0;
param koffieteamlid {k in koffieteams, s in schenkers}, binary;
param koffieteamritmegewenst {k in koffieteams}, >=0;
param gastvrouwritmegewenst {g in gastvrouwen}, >=0;

### variables ###

var leiding {l in leiders, z in zondagen}, binary;
var spelen {t in teams, z in zondagen}, binary;
var tegenzin {p in personen, z in zondagen}, binary; 
var teamlidmist {m in muzikanten, z in zondagen}, binary;
var teamuitritme {t in teams, z in zondagen}, binary;
var geluid {s in schuivers, z in zondagen}, binary;
var schuiveruitritme {s in schuivers, z in zondagen}, binary;
var beaming {b in beamers, z in zondagen}, binary;
var beameruitritme {b in beamers, z in zondagen}, binary;
var leiding_blauw {l in leiders_blauw, z in zondagen}, binary;
var blauwuitritme {l in leiders_blauw, z in zondagen}, binary;
var helpend_blauw {h in helpers_blauw, z in zondagen}, binary;
var nietvoorkeurpaar_blauw {z in zondagen}, binary;
var leiding_wit {l in leiders_wit, z in zondagen}, binary;
var wituitritme {l in leiders_wit, z in zondagen}, binary;
var helpend_wit {h in helpers_wit, z in zondagen}, binary;
var nietvoorkeurpaar_wit {z in zondagen}, binary;
var leiding_rood {l in leiders_rood, z in zondagen}, binary;
var rooduitritme {l in leiders_rood, z in zondagen}, binary;
var schenkendteam {k in koffieteams, z in zondagen}, binary;
var koffieteamuitritme {k in koffieteams, z in zondagen}, binary;
var welkom {g in gastvrouwen, z in zondagen}, binary;
var gastvrouwuitritme {g in gastvrouwen, z in zondagen}, binary;

### objective ###

minimize afwijkingen:
    (sum {m in muzikanten, z in zondagen} teamlidmist[m,z]*teamlidmisbaar[m])
    + (sum {p in personen, z in zondagen} 3*tegenzin[p,z])
    + (sum {t in teams, z in zondagen} 6*teamuitritme[t,z])
    + (sum {s in schuivers, z in zondagen} 3*schuiveruitritme[s,z])
    + (sum {b in beamers, z in zondagen} 3*beameruitritme[b,z])
    + (sum {l in leiders_blauw, z in zondagen} 3*blauwuitritme[l,z])
    + (sum {z in zondagen} 2*nietvoorkeurpaar_blauw[z])
    + (sum {l in leiders_wit, z in zondagen} 3*wituitritme[l,z])
    + (sum {z in zondagen} 2*nietvoorkeurpaar_wit[z])
    + (sum {l in leiders_rood, z in zondagen} 3*rooduitritme[l,z])
    + (sum {k in koffieteams, z in zondagen} 3*koffieteamuitritme[k,z])
    + (sum {g in gastvrouwen, z in zondagen} 3*gastvrouwuitritme[g,z])
;

### constraints ###

subject to een_leider
    {z in zondagen}:
	(sum {l in leiders} leiding[l,z]) = 1;
	
subject to leider_beschikbaar
    {z in zondagen, l in leiders}:
	leiding[l,z] <= beschikbaar[l,z] + 0.5 * tegenzin[l,z];
		
subject to een_leider_leidt_een_minimaal_aantal_maal
    {l in leiders}:
    (sum {z in zondagen} leiding[l,z]) >= leiderminimum[l];
        
subject to een_leider_leidt_een_maximaal_aantal_maal
    {l in leiders}:
    (sum {z in zondagen} leiding[l,z]) <= leidermaximum[l];
        
subject to een_leider_heeft_steeds_een_minimale_rust
    {l in leiders, z1 in zondagen: z1 <= laatste_week - leiderrust[l]}:
    (sum {z2 in z1..(z1+leiderrust[l])} leiding[l,z2]) <= 1;


        
subject to een_team
    {z in zondagen}:
    (sum {t in teams} spelen[t,z]) = 1;
		
subject to onmisbare_leden_beschikbaar
    {z in zondagen, t in teams, m in muzikanten: teamlid[t,m]=1 and teamlidmisbaar[m]=0}:
	spelen[t,z] <= beschikbaar[m,z] + 0.5 * tegenzin[m,z];
		
subject to misbare_leden_beschikbaar
    {z in zondagen, t in teams, m in muzikanten: teamlid[t,m]=1 and teamlidmisbaar[m]>=1}:
	spelen[t,z] <= beschikbaar[m,z] + teamlidmist[m,z];
		
subject to elk_team_speelt_een_minimaal_aantal_maal
    {t in teams}:
    (sum {z in zondagen} spelen[t,z]) >= teamminimum[t];
        
subject to elk_team_speelt_een_maximaal_aantal_maal
    {t in teams}:
    (sum {z in zondagen} spelen[t,z]) <= teammaximum[t];
        
subject to een_team_heeft_steeds_een_minimale_rust
    {t in teams, z1 in zondagen: z1 <= (laatste_week - teamrustminimum[t])}:
    (sum {z2 in z1..(z1+teamrustminimum[t])} spelen[t,z2]) <= 1;

subject to een_team_heeft_gewenste_ritme
    {t in teams, z1 in zondagen: z1 <= laatste_week - teamritmegewenst[t] + 1}:
    (sum {z2 in z1..(z1 + teamritmegewenst[t] - 1)} spelen[t,z2]) <= 1 + teamuitritme[t,z1];
        
subject to niet_teveel_missende_kwaliteit_in_een_team
    {z in zondagen}:
    (sum {m in muzikanten} teamlidmist[m,z]*teamlidmisbaar[m]) <= 3;

subject to een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_zn_eigen_team
    {l in dubbelleiders, z in zondagen}:
    spelen[l,z] >= leiding[l,z];



subject to een_schuiver
    {z in zondagen}:
	(sum {s in schuivers} geluid[s,z]) = 1;

subject to schuiver_beschikbaar
    {z in zondagen, s in schuivers}:
	geluid[s,z] <= beschikbaar[s,z];

subject to een_schuiver_heeft_gewenste_ritme
    {s in schuivers, z1 in zondagen: z1 <= laatste_week - schuiverritmegewenst[s] + 1}:
    (sum {z2 in z1..(z1 + schuiverritmegewenst[s] - 1)} geluid[s,z2]) <= 1 + schuiveruitritme[s,z1];



subject to een_beamer
    {z in zondagen}:
	(sum {b in beamers} beaming[b,z]) = 1;

subject to beamer_beschikbaar
    {z in zondagen, b in beamers}:
	beaming[b,z] <= beschikbaar[b,z];

subject to een_beamer_heeft_gewenste_ritme
    {b in beamers, z1 in zondagen: z1 <= laatste_week - beamerritmegewenst[b] + 1}:
    (sum {z2 in z1..(z1 + beamerritmegewenst[b] - 1)} beaming[b,z2]) <= 1 + beameruitritme[b,z1];



subject to een_leider_blauw
    {z in zondagen}:
	(sum {l in leiders_blauw} leiding_blauw[l,z]) = 1;

subject to leider_blauw_beschikbaar
    {z in zondagen, l in leiders_blauw}:
	leiding_blauw[l,z] <= beschikbaar[l,z];

subject to een_leider_blauw_heeft_gewenste_ritme
    {l in leiders_blauw, z1 in zondagen: z1 <= laatste_week - blauwritmegewenst[l] + 1}:
    (sum {z2 in z1..(z1 + blauwritmegewenst[l] - 1)} leiding_blauw[l,z2]) <= 1 + blauwuitritme[l,z1];

subject to een_helper_blauw
    {z in zondagen}:
	(sum {h in helpers_blauw} helpend_blauw[h,z]) = 1;

subject to helper_blauw_beschikbaar
    {z in zondagen, h in helpers_blauw}:
	helpend_blauw[h,z] <= beschikbaar[h,z];

subject to liefst_voorkeurparen_blauw
    {z in zondagen, l in leiders_blauw, h in helpers_blauw}:
	leiding_blauw[l,z] + helpend_blauw[h,z] <= 1 + voorkeurpaar_blauw[l,h] + nietvoorkeurpaar_blauw[z];



subject to een_leider_wit
    {z in zondagen}:
	(sum {l in leiders_wit} leiding_wit[l,z]) = 1;

subject to leider_wit_beschikbaar
    {z in zondagen, l in leiders_wit}:
	leiding_wit[l,z] <= beschikbaar[l,z];

subject to een_leider_wit_heeft_gewenste_ritme
    {l in leiders_wit, z1 in zondagen: z1 <= laatste_week - witritmegewenst[l] + 1}:
    (sum {z2 in z1..(z1 + witritmegewenst[l] - 1)} leiding_wit[l,z2]) <= 1 + wituitritme[l,z1];

subject to een_helper_wit
    {z in zondagen}:
	(sum {h in helpers_wit} helpend_wit[h,z]) = 1;

subject to helper_wit_beschikbaar
    {z in zondagen, h in helpers_wit}:
	helpend_wit[h,z] <= beschikbaar[h,z];

subject to liefst_voorkeurparen_wit
    {z in zondagen, l in leiders_wit, h in helpers_wit}:
	leiding_wit[l,z] + helpend_wit[h,z] <= 1 + voorkeurpaar_wit[l,h] + nietvoorkeurpaar_wit[z];



subject to een_leider_rood
    {z in zondagen}:
	(sum {l in leiders_rood} leiding_rood[l,z]) = 1;

subject to leider_rood_beschikbaar
    {z in zondagen, l in leiders_rood}:
	leiding_rood[l,z] <= beschikbaar[l,z];

subject to een_leider_rood_heeft_gewenste_ritme
    {l in leiders_rood, z1 in zondagen: z1 <= laatste_week - roodritmegewenst[l] + 1}:
    (sum {z2 in z1..(z1 + roodritmegewenst[l] - 1)} leiding_rood[l,z2]) <= 1 + rooduitritme[l,z1];


        
subject to een_koffieteam
    {z in zondagen}:
    (sum {k in koffieteams} schenkendteam[k,z]) = 1;
		
subject to koffieleden_beschikbaar
    {z in zondagen, k in koffieteams, s in schenkers: koffieteamlid[k,s]=1}:
	schenkendteam[k,z] <= beschikbaar[s,z];
		
subject to een_koffieteam_heeft_gewenste_ritme
    {k in koffieteams, z1 in zondagen: z1 <= laatste_week - koffieteamritmegewenst[k] + 1}:
    (sum {z2 in z1..(z1 + koffieteamritmegewenst[k] - 1)} schenkendteam[k,z2]) <= 1 + koffieteamuitritme[k,z1];



subject to een_gastvrouw
    {z in zondagen}:
	(sum {g in gastvrouwen} welkom[g,z]) = 1;

subject to gastvrouw_beschikbaar
    {z in zondagen, g in gastvrouwen}:
	welkom[g,z] <= beschikbaar[g,z];

subject to een_gastvrouw_heeft_gewenste_ritme
    {g in gastvrouwen, z1 in zondagen: z1 <= laatste_week - gastvrouwritmegewenst[g] + 1}:
    (sum {z2 in z1..(z1 + gastvrouwritmegewenst[g] - 1)} welkom[g,z2]) <= 1 + gastvrouwuitritme[g,z1];
    



subject to geen_geluid_en_leiding_tegelijk
    {p in leiders inter schuivers, z in zondagen}:
    geluid[p,z] + leiding[p,z] <= 1;
	
subject to geen_beamer_en_geluid_tegelijk
    {p in beamers inter schuivers, z in zondagen}:
    beaming[p,z] + geluid[p,z] <= 1;

subject to geen_beamer_en_muziek_tegelijk
    {p in beamers inter muzikanten, z in zondagen, t in teams: teamlid[t,p]=1}:
    beaming[p,z] + spelen[t,z] <= 1;

subject to geen_beamer_en_blauw_tegelijk
    {p in beamers inter helpers_blauw, z in zondagen}:
    beaming[p,z] + helpend_blauw[p,z] <= 1;

subject to geen_geluid_en_blauw_tegelijk
    {p in schuivers inter helpers_blauw, z in zondagen}:
    geluid[p,z] + helpend_blauw[p,z] <= 1;
	
subject to geen_beamer_en_wit_tegelijk
    {p in beamers inter helpers_wit, z in zondagen}:
    beaming[p,z] + helpend_wit[p,z] <= 1;

subject to geen_wit_en_blauw_tegelijk
    {p in helpers_wit inter helpers_blauw, z in zondagen}:
    helpend_wit[p,z] + helpend_blauw[p,z] <= 1;

subject to geen_leiding_en_rood_tegelijk
    {p in leiders inter leiders_rood, z in zondagen}:
    leiding[p,z] + leiding_rood[p,z] <= 1;

subject to geen_blauw_en_koffie_tegelijk
    {p in leiders_blauw inter schenkers, k in koffieteams, z in zondagen: koffieteamlid[k,p]=1}:
    leiding_blauw[p,z] + schenkendteam[k,z] <= 1;

subject to geen_muziek_en_welkom_tegelijk
    {p in muzikanten inter gastvrouwen, t in teams, z in zondagen: teamlid[t,p]=1}:
    spelen[t,z] + welkom[p,z] <= 1;

solve ;

display {z in zondagen, team in teams: spelen[team,z] = 1}: z, team;
display {z in zondagen, leider in leiders: leiding[leider,z] = 1}: z, leider;
display {z in zondagen, missendteamlid in muzikanten: teamlidmist[missendteamlid,z] = 1}: z, missendteamlid;
display {z in zondagen, mettegenzin in personen: tegenzin[mettegenzin,z] = 1}: z, mettegenzin;
display {z in zondagen, schuiver in schuivers: geluid[schuiver,z] = 1}: z, schuiver;
display {z in zondagen, beamer in beamers: beaming[beamer,z] = 1}: z, beamer;
display {z in zondagen, leider_blauw in leiders_blauw: leiding_blauw[leider_blauw,z] = 1}: z, leider_blauw;
display {z in zondagen, helper_blauw in helpers_blauw: helpend_blauw[helper_blauw,z] = 1}: z, helper_blauw;
display {z in zondagen: nietvoorkeurpaar_blauw[z] = 1}: z, 'nietvoorkeurpaar_blauw';
display {z in zondagen, leider_wit in leiders_wit: leiding_wit[leider_wit,z] = 1}: z, leider_wit;
display {z in zondagen, helper_wit in helpers_wit: helpend_wit[helper_wit,z] = 1}: z, helper_wit;
display {z in zondagen: nietvoorkeurpaar_wit[z] = 1}: z, 'nietvoorkeurpaar_wit';
display {z in zondagen, leider_rood in leiders_rood: leiding_rood[leider_rood,z] = 1}: z, leider_rood;
display {z in zondagen, koffie in koffieteams: schenkendteam[koffie,z] = 1}: z, koffie;
display {z in zondagen, gastvrouw in gastvrouwen: welkom[gastvrouw,z] = 1}: z, gastvrouw;

end;
