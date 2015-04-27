# Plannen van het Ichthus-rooster
#

### sets ###

set muzikanten;
set teams within muzikanten;
set leiders;
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
set kosters;
set hulpkosters;

set personen := muzikanten union leiders union schuivers union beamers union blauw union wit union rood 
                union schenkers union gastvrouwen union kosters union hulpkosters;

### parameters ###

param eerste_week, integer, >= 1;
param laatste_week, integer, >= eerste_week, <= 53;
param aantal_weken := laatste_week-eerste_week+1;
set zondagen := eerste_week .. laatste_week;
set zondagen_uitgebreid := (eerste_week-11)..(laatste_week+11);
param beschikbaar {p in personen, z in zondagen}, >=0, <=1;
param teamlid {t in teams, m in muzikanten}, binary;
param teamlidmisbaar {m in muzikanten}, >=0;
param teamritme {t in teams}, >=0;
param teamrust {t in teams}, >=0;
param leiderritme {l in leiders}, >=0;
param leiderrust {l in leiders}, >=0;
param schuiverritme {s in schuivers}, >=0;
param schuiverrust {schuivers}, >= 0;
param beamerritme {b in beamers}, >=0;
param beamerrust {beamers}, >=0;
param blauwritme {l in leiders_blauw}, >=0;
param blauwrust {l in leiders_blauw}, >=0;
param voorkeurpaar_blauw {l in leiders_blauw, h in helpers_blauw}, binary;
param witritme {l in leiders_wit}, >=0;
param witrust {leiders_wit}, >=0;
param voorkeurpaar_wit {l in leiders_wit, h in helpers_wit}, binary;
param roodritme {l in leiders_rood}, >=0;
param roodrust {l in leiders_rood}, >=0;
param koffieteamlid {k in koffieteams, s in schenkers}, binary;
param koffieritme {k in koffieteams}, >=0;
param koffierust {koffieteams}, >=0;
param gastvrouwritme {g in gastvrouwen}, >=0;
param gastvrouwrust {gastvrouwen}, >=0;
param kosterritme {k in kosters}, >=0;
param kosterrust {kosters}, >=0;
param hulpkosterritme {hulpkosters}, >=0;
param hulpkosterrust {hulpkosters}, >=0;

### variables ###

var leiding {l in leiders, z in zondagen}, binary;
var leideruitritme {l in leiders, z in zondagen_uitgebreid}, binary;
var spelen {t in teams, z in zondagen}, binary;
var tegenzin {p in personen, z in zondagen}, binary; 
var teamlidmist {m in muzikanten, z in zondagen}, binary;
var teamuitritme {t in teams, z in zondagen_uitgebreid}, binary;
var geluid {s in schuivers, z in zondagen}, binary;
var schuiveruitritme {s in schuivers, z in zondagen_uitgebreid}, binary;
var beaming {b in beamers, z in zondagen}, binary;
var beameruitritme {b in beamers, z in zondagen_uitgebreid}, binary;
var leiding_blauw {l in leiders_blauw, z in zondagen}, binary;
var blauwuitritme {l in leiders_blauw, z in zondagen_uitgebreid}, binary;
var helpend_blauw {h in helpers_blauw, z in zondagen}, binary;
var nietvoorkeurpaar_blauw {z in zondagen}, binary;
var leiding_wit {l in leiders_wit, z in zondagen}, binary;
var wituitritme {l in leiders_wit, z in zondagen_uitgebreid}, binary;
var helpend_wit {h in helpers_wit, z in zondagen}, binary;
var nietvoorkeurpaar_wit {z in zondagen}, binary;
var leiding_rood {l in leiders_rood, z in zondagen}, binary;
var rooduitritme {l in leiders_rood, z in zondagen_uitgebreid}, binary;
var schenkendteam {k in koffieteams, z in zondagen}, binary;
var koffieteamuitritme {k in koffieteams, z in zondagen_uitgebreid}, binary;
var welkom {g in gastvrouwen, z in zondagen}, binary;
var gastvrouwuitritme {g in gastvrouwen, z in zondagen_uitgebreid}, binary;
var kosterdienst {k in kosters, z in zondagen}, binary;
var kosteruitritme {k in kosters, z in zondagen_uitgebreid}, binary;
var hulpkosterdienst {h in hulpkosters, z in zondagen}, binary;
var hulpkosteruitritme {hulpkosters, zondagen_uitgebreid}, binary;
var wijngaardenbreuk {zondagen}, binary;
var timofrachel {zondagen}, binary;
var liannezondermatthijs, binary;
var matthijszonderlianne, binary;

### objective ###

minimize afwijkingen:
    (sum {m in muzikanten, z in zondagen} teamlidmist[m,z]*teamlidmisbaar[m])
    + (sum {p in personen, z in zondagen} 20*tegenzin[p,z])
    + (sum {t in teams, z in zondagen_uitgebreid} 8*teamuitritme[t,z])
    + (sum {l in leiders, z in zondagen_uitgebreid} 6*leideruitritme[l,z])
    + (sum {s in schuivers, z in zondagen_uitgebreid} 5*schuiveruitritme[s,z])
    + (sum {b in beamers, z in zondagen_uitgebreid} 3*beameruitritme[b,z])
    + (sum {l in leiders_blauw, z in zondagen_uitgebreid} 4*blauwuitritme[l,z])
    + (sum {z in zondagen} 6*nietvoorkeurpaar_blauw[z])
    + (sum {l in leiders_wit, z in zondagen_uitgebreid} 4*wituitritme[l,z])
    + (sum {z in zondagen} 100*nietvoorkeurpaar_wit[z])
    + (sum {l in leiders_rood, z in zondagen_uitgebreid} 1*rooduitritme[l,z])
    + (sum {k in koffieteams, z in zondagen_uitgebreid} 3*koffieteamuitritme[k,z])
    + (sum {g in gastvrouwen, z in zondagen_uitgebreid} 2*gastvrouwuitritme[g,z])
    + (sum {k in kosters, z in zondagen_uitgebreid} 8*kosteruitritme[k,z])
    + (sum {h in hulpkosters, z in zondagen_uitgebreid} 4*hulpkosteruitritme[h,z])
    + (sum {z in zondagen} 4*wijngaardenbreuk[z])
    + 10*matthijszonderlianne + 20*liannezondermatthijs
;

### constraints ###

subject to een_leider
    {z in zondagen}:
	(sum {l in leiders} leiding[l,z]) = 1;
	
subject to leider_beschikbaar
    {z in zondagen, l in leiders}:
	leiding[l,z] <= beschikbaar[l,z] + 0.5 * tegenzin[l,z];
		
subject to een_leider_heeft_gewenste_ritme
    {l in leiders, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + leiderritme[l] - 1): z2 in zondagen} leiding[l,z2])
        <= 1 + leideruitritme[l,z1];

subject to een_leider_leidt_een_minimaal_aantal_maal
    {l in leiders}:
    (sum {z in zondagen} leiding[l,z]) >= aantal_weken/leiderritme[l]-1;
        
subject to een_leider_leidt_een_maximaal_aantal_maal
    {l in leiders}:
    (sum {z in zondagen} leiding[l,z]) <= aantal_weken/leiderritme[l]+1;
        
subject to een_leider_heeft_steeds_een_minimale_rust
    {l in leiders, z1 in zondagen}:
    (sum {z2 in z1..(z1+leiderrust[l]): z2 in zondagen} leiding[l,z2]) <= 1;

        

      
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
    (sum {z in zondagen} spelen[t,z]) >= aantal_weken/teamritme[t]-1;
        
subject to elk_team_speelt_een_maximaal_aantal_maal
    {t in teams}:
    (sum {z in zondagen} spelen[t,z]) <= aantal_weken/teamritme[t]+1;
        
subject to een_team_heeft_steeds_een_minimale_rust
    {t in teams, z1 in zondagen}:
    (sum {z2 in z1..(z1+teamrust[t]): z2 in zondagen} spelen[t,z2]) <= 1;

subject to een_team_heeft_gewenste_ritme
    {t in teams, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + teamritme[t]-1):z2 in zondagen} spelen[t,z2])
        <= 1 + teamuitritme[t,z1];
        
subject to niet_teveel_missende_kwaliteit_in_een_team
    {z in zondagen}:
    (sum {m in muzikanten} teamlidmist[m,z]*teamlidmisbaar[m]) <= 3;

subject to een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_zn_eigen_team
    {p in leiders inter teams, z in zondagen}:
    spelen[p,z] >= leiding[p,z];



subject to een_schuiver
    {z in zondagen}:
	(sum {s in schuivers} geluid[s,z]) = 1;

subject to schuiver_beschikbaar
    {z in zondagen, s in schuivers}:
	geluid[s,z] <= beschikbaar[s,z];

subject to een_schuiver_heeft_gewenste_ritme
    {s in schuivers, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + schuiverritme[s] - 1): z2 in zondagen} geluid[s,z2])
        <= 1 + schuiveruitritme[s,z1];

subject to een_schuiver_schuift_een_minimaal_aantal_maal
    {s in schuivers}:
    (sum {z in zondagen} geluid[s,z]) >= aantal_weken/schuiverritme[s]-1;
        
subject to een_schuiver_schuift_een_maximaal_aantal_maal
    {s in schuivers}:
    (sum {z in zondagen} geluid[s,z]) <= aantal_weken/schuiverritme[s]+1;

subject to een_schuiver_heeft_steeds_een_minimale_rust
    {s in schuivers, z1 in zondagen}:
    (sum {z2 in z1..(z1+schuiverrust[s]): z2 in zondagen} geluid[s,z2]) <= 1;



subject to een_beamer
    {z in zondagen}:
	(sum {b in beamers} beaming[b,z]) = 1;

subject to beamer_beschikbaar
    {z in zondagen, b in beamers}:
	beaming[b,z] <= beschikbaar[b,z];

subject to een_beamer_heeft_gewenste_ritme
    {b in beamers, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + beamerritme[b]-1): z2 in zondagen} beaming[b,z2])
        <= 1 + beameruitritme[b,z1];

subject to een_beamer_beamt_een_minimaal_aantal_maal
    {b in beamers}:
    (sum {z in zondagen} beaming[b,z]) >= aantal_weken/beamerritme[b]-1;
        
subject to een_beamer_beamt_een_maximaal_aantal_maal
    {b in beamers}:
    (sum {z in zondagen} beaming[b,z]) <= aantal_weken/beamerritme[b]+1;

subject to een_beamer_heeft_steeds_een_minimale_rust
    {b in beamers, z1 in zondagen}:
    (sum {z2 in z1..(z1+beamerrust[b]): z2 in zondagen} beaming[b,z2]) <= 1;



subject to een_leider_blauw
    {z in zondagen}:
	(sum {l in leiders_blauw} leiding_blauw[l,z]) = 1;

subject to leider_blauw_beschikbaar
    {z in zondagen, l in leiders_blauw}:
	leiding_blauw[l,z] <= beschikbaar[l,z];

subject to een_leider_blauw_heeft_gewenste_ritme
    {l in leiders_blauw, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + blauwritme[l]-1): z2 in zondagen} leiding_blauw[l,z2])
        <= 1 + blauwuitritme[l,z1];

subject to een_leider_blauw_leidt_een_minimaal_aantal_maal
    {l in leiders_blauw}:
    (sum {z in zondagen} leiding_blauw[l,z]) >= aantal_weken/blauwritme[l]-1;
        
subject to een_leider_blauw_leidt_een_maximaal_aantal_maal
    {l in leiders_blauw}:
    (sum {z in zondagen} leiding_blauw[l,z]) <= aantal_weken/blauwritme[l]+1;
    
subject to een_leider_blauw_heeft_steeds_een_minimale_rust
    {l in leiders_blauw, z1 in zondagen}:
    (sum {z2 in z1..(z1+blauwrust[l]): z2 in zondagen} leiding_blauw[l,z2]) <= 1;
        
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
    {l in leiders_wit, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + witritme[l]-1): z2 in zondagen} leiding_wit[l,z2])
        <= 1 + wituitritme[l,z1];

subject to een_leider_wit_leidt_een_minimaal_aantal_maal
    {l in leiders_wit}:
    (sum {z in zondagen} leiding_wit[l,z]) >= aantal_weken/witritme[l]-1;
        
subject to een_leider_wit_leidt_een_maximaal_aantal_maal
    {l in leiders_wit}:
    (sum {z in zondagen} leiding_wit[l,z]) <= aantal_weken/witritme[l]+1;
    
subject to een_leider_wit_heeft_steeds_een_minimale_rust
    {l in leiders_wit, z1 in zondagen}:
    (sum {z2 in z1..(z1+witrust[l]): z2 in zondagen} leiding_wit[l,z2]) <= 1;

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
    {l in leiders_rood, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + roodritme[l] - 1): z2 in zondagen} leiding_rood[l,z2])
        <= 1 + rooduitritme[l,z1];

subject to een_leider_rood_leidt_een_minimaal_aantal_maal
    {l in leiders_rood}:
    (sum {z in zondagen} leiding_rood[l,z]) >= aantal_weken/roodritme[l]-2;
        
subject to een_leider_rood_leidt_een_maximaal_aantal_maal
    {l in leiders_rood}:
    (sum {z in zondagen} leiding_rood[l,z]) <= aantal_weken/roodritme[l]+1;

subject to een_leider_rood_heeft_steeds_een_minimale_rust
    {l in leiders_rood, z1 in zondagen}:
    (sum {z2 in z1..(z1+roodrust[l]): z2 in zondagen} leiding_rood[l,z2]) <= 1;


        
subject to een_koffieteam
    {z in zondagen}:
    (sum {k in koffieteams} schenkendteam[k,z]) = 1;
		
subject to koffieleden_beschikbaar
    {z in zondagen, k in koffieteams, s in schenkers: koffieteamlid[k,s]=1}:
	schenkendteam[k,z] <= beschikbaar[s,z];
		
subject to een_koffieteam_heeft_gewenste_ritme
    {k in koffieteams, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + koffieritme[k]-1): z2 in zondagen} schenkendteam[k,z2])
        <= 1 + koffieteamuitritme[k,z1];

subject to een_koffieteam_leidt_een_minimaal_aantal_maal
    {k in koffieteams}:
    (sum {z in zondagen} schenkendteam[k,z]) >= aantal_weken/koffieritme[k]-1;
        
subject to een_koffieteam_leidt_een_maximaal_aantal_maal
    {k in koffieteams}:
    (sum {z in zondagen} schenkendteam[k,z]) <= aantal_weken/koffieritme[k]+1;

subject to een_koffieteam_heeft_steeds_een_minimale_rust
    {k in koffieteams, z1 in zondagen}:
    (sum {z2 in z1..(z1+koffierust[k]): z2 in zondagen} schenkendteam[k,z2]) <= 1;



subject to een_gastvrouw
    {z in zondagen}:
	(sum {g in gastvrouwen} welkom[g,z]) = 1;

subject to gastvrouw_beschikbaar
    {z in zondagen, g in gastvrouwen}:
	welkom[g,z] <= beschikbaar[g,z];

subject to een_gastvrouw_heeft_gewenste_ritme
    {g in gastvrouwen, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + gastvrouwritme[g]-1): z2 in zondagen} welkom[g,z2])
        <= 1 + gastvrouwuitritme[g,z1];

subject to een_gastvrouw_welkomt_een_minimaal_aantal_maal
    {g in gastvrouwen}:
    (sum {z in zondagen} welkom[g,z]) >= aantal_weken/gastvrouwritme[g]-2;
        
subject to een_gastvrouw_welkomt_een_maximaal_aantal_maal
    {g in gastvrouwen}:
    (sum {z in zondagen} welkom[g,z]) <= aantal_weken/gastvrouwritme[g]+2;

subject to een_gastvrouw_heeft_steeds_een_minimale_rust
    {g in gastvrouwen, z1 in zondagen: g!='lianne'}:
    (sum {z2 in z1..(z1+gastvrouwrust[g]): z2 in zondagen} welkom[g,z2]) <= 1;



subject to een_koster
    {z in zondagen}:
	(sum {k in kosters} kosterdienst[k,z]) = 1;

subject to koster_beschikbaar
    {z in zondagen, k in kosters}:
	kosterdienst[k,z] <= beschikbaar[k,z];

subject to een_koster_draait_dubbele_diensten
    {k in kosters, z in 0..(aantal_weken/2-1)}:
    kosterdienst[k,eerste_week+2*z] = kosterdienst[k,eerste_week+2*z+1];

subject to een_koster_heeft_gewenste_ritme
    {k in kosters, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + kosterritme[k]-1): z2 in zondagen} kosterdienst[k,z2])
        <= 2 + kosteruitritme[k,z1];

subject to een_koster_kostert_een_minimaal_aantal_maal
    {k in kosters}:
    (sum {z in zondagen} kosterdienst[k,z]) >= aantal_weken/kosterritme[k]-2;
        
subject to een_koster_kostert_een_maximaal_aantal_maal
    {k in kosters}:
    (sum {z in zondagen} kosterdienst[k,z]) <= aantal_weken/kosterritme[k]+2;

subject to een_koster_heeft_steeds_een_minimale_rust
    {k in kosters, z1 in zondagen}:
    (sum {z2 in z1..(z1+kosterrust[k]+1): z2 in zondagen} kosterdienst[k,z2]) <= 2;

subject to twee_hulpkosters
    {z in zondagen}:
	(sum {h in hulpkosters} hulpkosterdienst[h,z]) = 2;

subject to hulpkoster_beschikbaar
    {z in zondagen, h in hulpkosters}:
	hulpkosterdienst[h,z] <= beschikbaar[h,z];


subject to een_hulpkoster_heeft_gewenste_ritme
    {h in hulpkosters, z1 in zondagen_uitgebreid}:
    (sum {z2 in z1..(z1 + hulpkosterritme[h] - 1): z2 in zondagen} hulpkosterdienst[h,z2])
        <= 2 + hulpkosteruitritme[h,z1];

subject to een_hulpkoster_kostert_een_minimaal_aantal_maal
    {h in hulpkosters}:
    (sum {z in zondagen} hulpkosterdienst[h,z]) >= aantal_weken/hulpkosterritme[h]-2;
        
subject to een_hulpkoster_kostert_een_maximaal_aantal_maal
    {h in hulpkosters}:
    (sum {z in zondagen} hulpkosterdienst[h,z]) <= aantal_weken/hulpkosterritme[h]+2;

subject to een_hulpkoster_heeft_steeds_een_minimale_rust
    {h in hulpkosters, z1 in zondagen}:
    (sum {z2 in z1..(z1+hulpkosterrust[h]): z2 in zondagen} hulpkosterdienst[h,z2]) <= 1;



subject to geen_leiding_en_geluid_tegelijk
    {p in leiders inter schuivers, z in zondagen}:
    geluid[p,z] + leiding[p,z] <= 1;

subject to geen_leiding_en_rood_tegelijk
    {p in leiders inter leiders_rood, z in zondagen}:
    leiding[p,z] + leiding_rood[p,z] <= 1;

subject to geen_muziek_en_wit_tegelijk
    {p in muzikanten inter leiders_wit, t in teams, z in zondagen: teamlid[t,p]=1}:
    spelen[t,z] + leiding_wit[p,z] <= 1;

subject to geen_muziek_en_welkom_tegelijk
    {p in muzikanten inter gastvrouwen, t in teams, z in zondagen: teamlid[t,p]=1}:
    spelen[t,z] + welkom[p,z] <= 1;

subject to geen_muziek_en_hulpkoster_tegelijk
    {p in muzikanten inter hulpkosters, t in teams, z in zondagen: teamlid[t,p]=1}:
    spelen[t,z] + hulpkosterdienst[p,z] <= 1;
	
subject to geen_beamer_en_geluid_tegelijk
    {p in beamers inter schuivers, z in zondagen}:
    beaming[p,z] + geluid[p,z] <= 1;

subject to geen_beamer_en_muziek_tegelijk
    {p in beamers inter muzikanten, z in zondagen, t in teams: teamlid[t,p]=1}:
    beaming[p,z] + spelen[t,z] <= 1;

subject to geen_beamer_en_blauw_tegelijk
    {p in beamers inter helpers_blauw, z in zondagen}:
    beaming[p,z] + helpend_blauw[p,z] <= 1;
	
subject to geen_beamer_en_wit_tegelijk
    {p in beamers inter helpers_wit, z in zondagen}:
    beaming[p,z] + helpend_wit[p,z] <= 1;

subject to geen_geluid_en_blauw_tegelijk
    {p in schuivers inter helpers_blauw, z in zondagen}:
    geluid[p,z] + helpend_blauw[p,z] <= 1;

subject to geen_geluid_en_koster_tegelijk
    {p in schuivers inter kosters, z in zondagen}:
    geluid[p,z] + kosterdienst[p,z] <= 1;

subject to geen_blauw_en_wit_tegelijk
    {p in helpers_wit inter helpers_blauw, z in zondagen}:
    helpend_wit[p,z] + helpend_blauw[p,z] <= 1;

subject to geen_blauw_en_koffie_tegelijk
    {p in leiders_blauw inter schenkers, k in koffieteams, z in zondagen: koffieteamlid[k,p]=1}:
    leiding_blauw[p,z] + schenkendteam[k,z] <= 1;

subject to geen_blauw_en_welkom_tegelijk
    {p in leiders_blauw inter gastvrouwen, z in zondagen}:
    leiding_blauw[p,z] + welkom[p,z] <= 1;

subject to geen_wit_en_welkom_tegelijk
    {p in leiders_wit inter gastvrouwen, z in zondagen}:
    leiding_wit[p,z] + welkom[p,z] <= 1;

subject to geen_rood_en_welkom_tegelijk
    {p in leiders_rood inter gastvrouwen, z in zondagen}:
    leiding_rood[p,z] + welkom[p,z] <= 1;

subject to geen_leiding_rood_en_koffie_tegelijk
    {p in leiders_rood inter schenkers, k in koffieteams, z in zondagen: koffieteamlid[k,p]=1}:
    leiding_rood[p,z] + schenkendteam[k,z] <= 1;

subject to geen_leiding_rood_en_hulpkoster_tegelijk
    {p in leiders_rood inter hulpkosters, z in zondagen}:
    leiding_rood[p,z] + hulpkosterdienst[p,z] <= 1;

#ministry sluit kinderdienst, muziek, leiding en geluid uit

### vast ingedeeld ###
subject to rijswijk_special1 {z in zondagen}: kosterdienst['matthijs',z] <= welkom['lianne',z] + matthijszonderlianne;
subject to rijswijk_special2 {z in zondagen}: welkom['lianne',z] <= kosterdienst['matthijs',z] + liannezondermatthijs;
subject to wijngaarden_special {z in zondagen}: leiding_blauw['rachel',z] + leiding_rood['tim',z] = 2*timofrachel[z] - wijngaardenbreuk[z];
subject to rood14: leiding_rood['special',14] = 1;
subject to rood_special: (sum {z in zondagen:z!=14} leiding_rood['special',z]) = 0;
    
solve ;

display {z in zondagen, team in teams: spelen[team,z] = 1}: z, team;
display {z in zondagen, leider in leiders: leiding[leider,z] = 1}: z, leider;
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
display {z in zondagen, koster in kosters: kosterdienst[koster,z] = 1}: z, koster;
display {z in zondagen, hulpkoster in hulpkosters: hulpkosterdienst[hulpkoster,z] = 1}: z, hulpkoster;
display {z in zondagen, missendteamlid in muzikanten: teamlidmist[missendteamlid,z] = 1}: z, missendteamlid;
display {z in zondagen, mettegenzin in personen: tegenzin[mettegenzin,z] = 1}: z, mettegenzin;

end;
