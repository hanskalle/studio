# Plannen van het Ichthus-rooster voor het aanbiddingsteam
#

### sets ###

set muzikanten;
set teams within muzikanten;
set leiders;
set personen := muzikanten union leiders;
set dubbelleiders := teams inter leiders;

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

### variables ###

var leiding {l in leiders, z in zondagen}, binary;
var muziek {m in muzikanten, z in zondagen}, binary;
var spelen {t in teams, z in zondagen}, binary;
var tegenzin {p in personen, z in zondagen}, binary; 
var teamlidmist {m in muzikanten, z in zondagen}, binary;
var teamuitritme {t in teams, z in zondagen}, binary;

### objective ###

minimize afwijkingen:
    (sum {m in muzikanten, z in zondagen} teamlidmist[m,z]*teamlidmisbaar[m])
    + (sum {p in personen, z in zondagen} 3*tegenzin[p,z])
    + (sum {t in teams, z in zondagen} 6*teamuitritme[t,z]);

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
        
subject to een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_zn_eigen_team
    {l in dubbelleiders, z in zondagen}:
    spelen[l,z] >= leiding[l,z];

subject to niet_teveel_missende_kwaliteit_in_een_team
    {z in zondagen}:
    (sum {m in muzikanten} teamlidmist[m,z]*teamlidmisbaar[m]) <= 3;

solve ;

display {z in zondagen, team in teams: spelen[team,z] = 1}: z, team;
display {z in zondagen, leider in leiders: leiding[leider,z] = 1}: z, leider;
display {z in zondagen, missendteamlid in muzikanten: teamlidmist[missendteamlid,z] = 1}: z, missendteamlid;
display {z in zondagen, mettegenzin in personen: tegenzin[mettegenzin,z] = 1}: z, mettegenzin;

end;
