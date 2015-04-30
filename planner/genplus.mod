set Zangleiding_persons;
set Muziek_persons;
set Muziek_teams;
set Geluid_persons;
set Beamer_persons;
set Leiding_Rood_persons;
set Leiding_Wit_persons;
set Groep_Wit_persons;
set Leiding_Blauw_persons;
set Groep_Blauw_persons;
set Koffie_persons;
set Koffie_teams;
set Welkom_persons;
set Hoofdkoster_persons;
set Hulpkoster_persons;
param first_week, integer, >= 1;
param last_week, integer, <= 53;
param number_of_weeks := last_week - first_week+1;
set weeks := first_week .. last_week;
set weeks_extended := (first_week-number_of_weeks+2) .. (last_week+number_of_weeks-2);
param Zangleiding_offritme_penalty, >=0;
param Zangleiding_rather_not_penalty, >=0;
param Zangleiding_available {p in Zangleiding_persons, w in weeks}, >=0, <=1;
param Zangleiding_ritme {p in Zangleiding_persons}, integer, >=1;
param Zangleiding_rest {p in Zangleiding_persons}, integer, >=0;
param Muziek_offritme_penalty, >=0;
param Muziek_rather_not_penalty, >=0;
param Muziek_available {p in Muziek_persons, w in weeks}, >=0, <=1;
param Muziek_member {t in Muziek_teams, p in Muziek_persons}, binary;
param Muziek_essential {p in Muziek_persons}, >= 0;
param Muziek_maximum_missing {t in Muziek_teams}, >= 0;
param Muziek_ritme {p in Muziek_teams}, integer, >=1;
param Muziek_rest {p in Muziek_teams}, integer, >=0;
param Geluid_offritme_penalty, >=0;
param Geluid_rather_not_penalty, >=0;
param Geluid_available {p in Geluid_persons, w in weeks}, >=0, <=1;
param Geluid_ritme {p in Geluid_persons}, integer, >=1;
param Geluid_rest {p in Geluid_persons}, integer, >=0;
param Beamer_offritme_penalty, >=0;
param Beamer_rather_not_penalty, >=0;
param Beamer_available {p in Beamer_persons, w in weeks}, >=0, <=1;
param Beamer_ritme {p in Beamer_persons}, integer, >=1;
param Beamer_rest {p in Beamer_persons}, integer, >=0;
param Leiding_Rood_offritme_penalty, >=0;
param Leiding_Rood_rather_not_penalty, >=0;
param Leiding_Rood_available {p in Leiding_Rood_persons, w in weeks}, >=0, <=1;
param Leiding_Rood_ritme {p in Leiding_Rood_persons}, integer, >=1;
param Leiding_Rood_rest {p in Leiding_Rood_persons}, integer, >=0;
param Leiding_Wit_offritme_penalty, >=0;
param Leiding_Wit_rather_not_penalty, >=0;
param Leiding_Wit_available {p in Leiding_Wit_persons, w in weeks}, >=0, <=1;
param Leiding_Wit_ritme {p in Leiding_Wit_persons}, integer, >=1;
param Leiding_Wit_rest {p in Leiding_Wit_persons}, integer, >=0;
param Groep_Wit_offritme_penalty, >=0;
param Groep_Wit_rather_not_penalty, >=0;
param Groep_Wit_available {p in Groep_Wit_persons, w in weeks}, >=0, <=1;
param Groep_Wit_prefered_pair {p1 in Leiding_Wit_persons, p2 in Groep_Wit_persons}, binary;
param Groep_Wit_not_prefered_pair_penalty, >=0;
param Leiding_Blauw_offritme_penalty, >=0;
param Leiding_Blauw_rather_not_penalty, >=0;
param Leiding_Blauw_available {p in Leiding_Blauw_persons, w in weeks}, >=0, <=1;
param Leiding_Blauw_ritme {p in Leiding_Blauw_persons}, integer, >=1;
param Leiding_Blauw_rest {p in Leiding_Blauw_persons}, integer, >=0;
param Groep_Blauw_offritme_penalty, >=0;
param Groep_Blauw_rather_not_penalty, >=0;
param Groep_Blauw_available {p in Groep_Blauw_persons, w in weeks}, >=0, <=1;
param Groep_Blauw_prefered_pair {p1 in Leiding_Blauw_persons, p2 in Groep_Blauw_persons}, binary;
param Groep_Blauw_not_prefered_pair_penalty, >=0;
param Koffie_offritme_penalty, >=0;
param Koffie_rather_not_penalty, >=0;
param Koffie_available {p in Koffie_persons, w in weeks}, >=0, <=1;
param Koffie_member {t in Koffie_teams, p in Koffie_persons}, binary;
param Koffie_essential {p in Koffie_persons}, >= 0;
param Koffie_maximum_missing {t in Koffie_teams}, >= 0;
param Koffie_ritme {p in Koffie_teams}, integer, >=1;
param Koffie_rest {p in Koffie_teams}, integer, >=0;
param Welkom_offritme_penalty, >=0;
param Welkom_rather_not_penalty, >=0;
param Welkom_available {p in Welkom_persons, w in weeks}, >=0, <=1;
param Welkom_ritme {p in Welkom_persons}, integer, >=1;
param Welkom_rest {p in Welkom_persons}, integer, >=0;
param Hoofdkoster_offritme_penalty, >=0;
param Hoofdkoster_rather_not_penalty, >=0;
param Hoofdkoster_available {p in Hoofdkoster_persons, w in weeks}, >=0, <=1;
param Hoofdkoster_ritme {p in Hoofdkoster_persons}, integer, >=1;
param Hoofdkoster_rest {p in Hoofdkoster_persons}, integer, >=0;
param Hulpkoster_offritme_penalty, >=0;
param Hulpkoster_rather_not_penalty, >=0;
param Hulpkoster_available {p in Hulpkoster_persons, w in weeks}, >=0, <=1;
param Hulpkoster_ritme {p in Hulpkoster_persons}, integer, >=1;
param Hulpkoster_rest {p in Hulpkoster_persons}, integer, >=0;
var Zangleiding {t in Zangleiding_persons, w in weeks}, binary;
var Zangleiding_rather_not {p in Zangleiding_persons, w in weeks}, binary;
var Zangleiding_offritme {t in Zangleiding_persons, w in weeks_extended}, binary;
var Muziek {t in Muziek_teams, w in weeks}, binary;
var Muziek_rather_not {p in Muziek_persons, w in weeks}, binary;
var Muziek_missing {p in Muziek_persons, w in weeks}, binary;
var Muziek_offritme {t in Muziek_teams, w in weeks_extended}, binary;
var Geluid {t in Geluid_persons, w in weeks}, binary;
var Geluid_rather_not {p in Geluid_persons, w in weeks}, binary;
var Geluid_offritme {t in Geluid_persons, w in weeks_extended}, binary;
var Beamer {t in Beamer_persons, w in weeks}, binary;
var Beamer_rather_not {p in Beamer_persons, w in weeks}, binary;
var Beamer_offritme {t in Beamer_persons, w in weeks_extended}, binary;
var Leiding_Rood {t in Leiding_Rood_persons, w in weeks}, binary;
var Leiding_Rood_rather_not {p in Leiding_Rood_persons, w in weeks}, binary;
var Leiding_Rood_offritme {t in Leiding_Rood_persons, w in weeks_extended}, binary;
var Leiding_Wit {t in Leiding_Wit_persons, w in weeks}, binary;
var Leiding_Wit_rather_not {p in Leiding_Wit_persons, w in weeks}, binary;
var Leiding_Wit_offritme {t in Leiding_Wit_persons, w in weeks_extended}, binary;
var Groep_Wit {t in Groep_Wit_persons, w in weeks}, binary;
var Groep_Wit_rather_not {p in Groep_Wit_persons, w in weeks}, binary;
var Groep_Wit_not_prefered_pair {w in weeks}, binary;
var Leiding_Blauw {t in Leiding_Blauw_persons, w in weeks}, binary;
var Leiding_Blauw_rather_not {p in Leiding_Blauw_persons, w in weeks}, binary;
var Leiding_Blauw_offritme {t in Leiding_Blauw_persons, w in weeks_extended}, binary;
var Groep_Blauw {t in Groep_Blauw_persons, w in weeks}, binary;
var Groep_Blauw_rather_not {p in Groep_Blauw_persons, w in weeks}, binary;
var Groep_Blauw_not_prefered_pair {w in weeks}, binary;
var Koffie {t in Koffie_teams, w in weeks}, binary;
var Koffie_rather_not {p in Koffie_persons, w in weeks}, binary;
var Koffie_missing {p in Koffie_persons, w in weeks}, binary;
var Koffie_offritme {t in Koffie_teams, w in weeks_extended}, binary;
var Welkom {t in Welkom_persons, w in weeks}, binary;
var Welkom_rather_not {p in Welkom_persons, w in weeks}, binary;
var Welkom_offritme {t in Welkom_persons, w in weeks_extended}, binary;
var Hoofdkoster {t in Hoofdkoster_persons, w in weeks}, binary;
var Hoofdkoster_rather_not {p in Hoofdkoster_persons, w in weeks}, binary;
var Hoofdkoster_offritme {t in Hoofdkoster_persons, w in weeks_extended}, binary;
var Hulpkoster {t in Hulpkoster_persons, w in weeks}, binary;
var Hulpkoster_rather_not {p in Hulpkoster_persons, w in weeks}, binary;
var Hulpkoster_offritme {t in Hulpkoster_persons, w in weeks_extended}, binary;
# extra start
var timofrachel {weeks}, binary;
var wijngaardenbreuk {weeks}, binary;
var matthijszonderlianne, binary;
var liannezondermatthijs, binary;
# extra end
minimize penalties:
  + (sum {x in Zangleiding_persons, w in weeks_extended} Zangleiding_offritme_penalty * Zangleiding_offritme[x,w])
  + (sum {p in Zangleiding_persons, w in weeks} Zangleiding_rather_not_penalty * Zangleiding_rather_not[p,w])
  + (sum {x in Geluid_persons, w in weeks_extended} Geluid_offritme_penalty * Geluid_offritme[x,w])
  + (sum {p in Geluid_persons, w in weeks} Geluid_rather_not_penalty * Geluid_rather_not[p,w])
  + (sum {x in Beamer_persons, w in weeks_extended} Beamer_offritme_penalty * Beamer_offritme[x,w])
  + (sum {p in Beamer_persons, w in weeks} Beamer_rather_not_penalty * Beamer_rather_not[p,w])
  + (sum {x in Leiding_Rood_persons, w in weeks_extended} Leiding_Rood_offritme_penalty * Leiding_Rood_offritme[x,w])
  + (sum {p in Leiding_Rood_persons, w in weeks} Leiding_Rood_rather_not_penalty * Leiding_Rood_rather_not[p,w])
  + (sum {x in Welkom_persons, w in weeks_extended} Welkom_offritme_penalty * Welkom_offritme[x,w])
  + (sum {p in Welkom_persons, w in weeks} Welkom_rather_not_penalty * Welkom_rather_not[p,w])
  + (sum {x in Hoofdkoster_persons, w in weeks_extended} Hoofdkoster_offritme_penalty * Hoofdkoster_offritme[x,w])
  + (sum {p in Hoofdkoster_persons, w in weeks} Hoofdkoster_rather_not_penalty * Hoofdkoster_rather_not[p,w])
  + (sum {x in Hulpkoster_persons, w in weeks_extended} Hulpkoster_offritme_penalty * Hulpkoster_offritme[x,w])
  + (sum {p in Hulpkoster_persons, w in weeks} Hulpkoster_rather_not_penalty * Hulpkoster_rather_not[p,w])
  + (sum {x in Muziek_teams, w in weeks_extended} Muziek_offritme_penalty * Muziek_offritme[x,w])
  + (sum {p in Muziek_persons, w in weeks} Muziek_rather_not_penalty * Muziek_rather_not[p,w])
  + (sum {p in Muziek_persons, w in weeks} Muziek_essential[p] * Muziek_missing[p,w])
  + (sum {x in Koffie_teams, w in weeks_extended} Koffie_offritme_penalty * Koffie_offritme[x,w])
  + (sum {p in Koffie_persons, w in weeks} Koffie_rather_not_penalty * Koffie_rather_not[p,w])
  + (sum {p in Koffie_persons, w in weeks} Koffie_essential[p] * Koffie_missing[p,w])
  + (sum {x in Leiding_Blauw_persons, w in weeks_extended} Leiding_Blauw_offritme_penalty * Leiding_Blauw_offritme[x,w])
  + (sum {p in Groep_Blauw_persons, w in weeks} Groep_Blauw_rather_not_penalty * Groep_Blauw_rather_not[p,w])
  + (sum {w in weeks} Groep_Blauw_not_prefered_pair_penalty * Groep_Blauw_not_prefered_pair[w])
  + (sum {x in Leiding_Wit_persons, w in weeks_extended} Leiding_Wit_offritme_penalty * Leiding_Wit_offritme[x,w])
  + (sum {p in Groep_Wit_persons, w in weeks} Groep_Wit_rather_not_penalty * Groep_Wit_rather_not[p,w])
  + (sum {w in weeks} Groep_Wit_not_prefered_pair_penalty * Groep_Wit_not_prefered_pair[w])
# extra start
  + (sum {w in weeks} 4 * wijngaardenbreuk[w])
  + 10*matthijszonderlianne + 20*liannezondermatthijs
# extra end
;
subject to available_Zangleiding
  {w in weeks, p in Zangleiding_persons}:
  Zangleiding[p,w] <= Zangleiding_available[p,w] + 0.5 * Zangleiding_rather_not[p,w];
subject to single_Zangleiding
  {w in weeks}:
  (sum {x in Zangleiding_persons} Zangleiding[x,w]) = 1;
subject to ritme_Zangleiding
  {w1 in weeks_extended, x in Zangleiding_persons}:
  (sum {w2 in w1..(w1 + Zangleiding_ritme[x]-1): w2 in weeks} Zangleiding[x,w2])
    <= 1 + Zangleiding_offritme[x,w1];
subject to minimum_Zangleiding
  {x in Zangleiding_persons}:
  (sum {w in weeks} Zangleiding[x,w])
    >= number_of_weeks/Zangleiding_ritme[x]-2;
subject to maximum_Zangleiding
  {x in Zangleiding_persons}:
  (sum {w in weeks} Zangleiding[x,w])
    <= number_of_weeks/Zangleiding_ritme[x]+2;
subject to rest_Zangleiding
  {x in Zangleiding_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Zangleiding_rest[x]): w2 in weeks} Zangleiding[x,w2])
    <= 1;
subject to available_Geluid
  {w in weeks, p in Geluid_persons}:
  Geluid[p,w] <= Geluid_available[p,w] + 0.5 * Geluid_rather_not[p,w];
subject to single_Geluid
  {w in weeks}:
  (sum {x in Geluid_persons} Geluid[x,w]) = 1;
subject to ritme_Geluid
  {w1 in weeks_extended, x in Geluid_persons}:
  (sum {w2 in w1..(w1 + Geluid_ritme[x]-1): w2 in weeks} Geluid[x,w2])
    <= 1 + Geluid_offritme[x,w1];
subject to minimum_Geluid
  {x in Geluid_persons}:
  (sum {w in weeks} Geluid[x,w])
    >= number_of_weeks/Geluid_ritme[x]-2;
subject to maximum_Geluid
  {x in Geluid_persons}:
  (sum {w in weeks} Geluid[x,w])
    <= number_of_weeks/Geluid_ritme[x]+2;
subject to rest_Geluid
  {x in Geluid_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Geluid_rest[x]): w2 in weeks} Geluid[x,w2])
    <= 1;
subject to available_Beamer
  {w in weeks, p in Beamer_persons}:
  Beamer[p,w] <= Beamer_available[p,w] + 0.5 * Beamer_rather_not[p,w];
subject to single_Beamer
  {w in weeks}:
  (sum {x in Beamer_persons} Beamer[x,w]) = 1;
subject to ritme_Beamer
  {w1 in weeks_extended, x in Beamer_persons}:
  (sum {w2 in w1..(w1 + Beamer_ritme[x]-1): w2 in weeks} Beamer[x,w2])
    <= 1 + Beamer_offritme[x,w1];
subject to minimum_Beamer
  {x in Beamer_persons}:
  (sum {w in weeks} Beamer[x,w])
    >= number_of_weeks/Beamer_ritme[x]-2;
subject to maximum_Beamer
  {x in Beamer_persons}:
  (sum {w in weeks} Beamer[x,w])
    <= number_of_weeks/Beamer_ritme[x]+2;
subject to rest_Beamer
  {x in Beamer_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Beamer_rest[x]): w2 in weeks} Beamer[x,w2])
    <= 1;
subject to available_Leiding_Rood
  {w in weeks, p in Leiding_Rood_persons}:
  Leiding_Rood[p,w] <= Leiding_Rood_available[p,w] + 0.5 * Leiding_Rood_rather_not[p,w];
subject to single_Leiding_Rood
  {w in weeks}:
  (sum {x in Leiding_Rood_persons} Leiding_Rood[x,w]) = 1;
subject to ritme_Leiding_Rood
  {w1 in weeks_extended, x in Leiding_Rood_persons}:
  (sum {w2 in w1..(w1 + Leiding_Rood_ritme[x]-1): w2 in weeks} Leiding_Rood[x,w2])
    <= 1 + Leiding_Rood_offritme[x,w1];
subject to minimum_Leiding_Rood
  {x in Leiding_Rood_persons}:
  (sum {w in weeks} Leiding_Rood[x,w])
    >= number_of_weeks/Leiding_Rood_ritme[x]-2;
subject to maximum_Leiding_Rood
  {x in Leiding_Rood_persons}:
  (sum {w in weeks} Leiding_Rood[x,w])
    <= number_of_weeks/Leiding_Rood_ritme[x]+2;
subject to rest_Leiding_Rood
  {x in Leiding_Rood_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Leiding_Rood_rest[x]): w2 in weeks} Leiding_Rood[x,w2])
    <= 1;
subject to available_Welkom
  {w in weeks, p in Welkom_persons}:
  Welkom[p,w] <= Welkom_available[p,w] + 0.5 * Welkom_rather_not[p,w];
subject to single_Welkom
  {w in weeks}:
  (sum {x in Welkom_persons} Welkom[x,w]) = 1;
subject to ritme_Welkom
  {w1 in weeks_extended, x in Welkom_persons}:
  (sum {w2 in w1..(w1 + Welkom_ritme[x]-1): w2 in weeks} Welkom[x,w2])
    <= 1 + Welkom_offritme[x,w1];
subject to minimum_Welkom
  {x in Welkom_persons}:
  (sum {w in weeks} Welkom[x,w])
    >= number_of_weeks/Welkom_ritme[x]-2;
subject to maximum_Welkom
  {x in Welkom_persons}:
  (sum {w in weeks} Welkom[x,w])
    <= number_of_weeks/Welkom_ritme[x]+2;
subject to rest_Welkom
  {x in Welkom_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Welkom_rest[x]): w2 in weeks} Welkom[x,w2])
    <= 1;
subject to available_Hoofdkoster
  {w in weeks, p in Hoofdkoster_persons}:
  Hoofdkoster[p,w] <= Hoofdkoster_available[p,w] + 0.5 * Hoofdkoster_rather_not[p,w];
subject to single_Hoofdkoster
  {w in weeks}:
  (sum {x in Hoofdkoster_persons} Hoofdkoster[x,w]) = 1;
# extra aanpassing start
subject to ritme_Hoofdkoster
  {w1 in weeks_extended, x in Hoofdkoster_persons}:
  (sum {w2 in w1..(w1 + Hoofdkoster_ritme[x]-1): w2 in weeks} Hoofdkoster[x,w2])
    <= 2 + Hoofdkoster_offritme[x,w1]; # 2 ipv 1
# extra aanpasing end
# extra start
subject to dubbele_diensten_Hoofdkoster
    {p in Hoofdkoster_persons, w in 0..(number_of_weeks/2-1): (first_week+2*w+1) in weeks}:
    Hoofdkoster[p,first_week+2*w] = Hoofdkoster[p,first_week+2*w+1]; # extra regel
# extra end
subject to minimum_Hoofdkoster
  {x in Hoofdkoster_persons}:
  (sum {w in weeks} Hoofdkoster[x,w])
    >= number_of_weeks/Hoofdkoster_ritme[x]-2;
subject to maximum_Hoofdkoster
  {x in Hoofdkoster_persons}:
  (sum {w in weeks} Hoofdkoster[x,w])
    <= number_of_weeks/Hoofdkoster_ritme[x]+2;
# extra aanpassing start
subject to rest_Hoofdkoster
  {x in Hoofdkoster_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Hoofdkoster_rest[x] + 1): w2 in weeks} Hoofdkoster[x,w2])
    <= 2;
# extra aanpassing end
subject to available_Hulpkoster
  {w in weeks, p in Hulpkoster_persons}:
  Hulpkoster[p,w] <= Hulpkoster_available[p,w] + 0.5 * Hulpkoster_rather_not[p,w];
# extra aanpassing start
subject to double_Hulpkoster
  {w in weeks}:
  (sum {x in Hulpkoster_persons} Hulpkoster[x,w]) = 2; # 2 ipv 1
# extra aanpassing end
subject to ritme_Hulpkoster
  {w1 in weeks_extended, x in Hulpkoster_persons}:
  (sum {w2 in w1..(w1 + Hulpkoster_ritme[x]-1): w2 in weeks} Hulpkoster[x,w2])
    <= 1 + Hulpkoster_offritme[x,w1];
subject to minimum_Hulpkoster
  {x in Hulpkoster_persons}:
  (sum {w in weeks} Hulpkoster[x,w])
    >= number_of_weeks/Hulpkoster_ritme[x]-2;
subject to maximum_Hulpkoster
  {x in Hulpkoster_persons}:
  (sum {w in weeks} Hulpkoster[x,w])
    <= number_of_weeks/Hulpkoster_ritme[x]+2;
subject to rest_Hulpkoster
  {x in Hulpkoster_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Hulpkoster_rest[x]): w2 in weeks} Hulpkoster[x,w2])
    <= 1;
subject to available_Muziek
  {w in weeks, t in Muziek_teams, p in Muziek_persons: Muziek_member[t,p]=1 and Muziek_essential[p]=0}:
  Muziek[t,w] <= Muziek_available[p,w] + 0.5 * Muziek_rather_not[p,w];
subject to missing_Muziek
  {w in weeks, t in Muziek_teams, p in Muziek_persons: Muziek_member[t,p]=1 and Muziek_essential[p]>=1}:
  Muziek[t,w] <= Muziek_available[p,w] + Muziek_missing[p,w];
subject to maximum_missing_Muziek
  {w in weeks, t in Muziek_teams}:
  (sum {p in Muziek_persons: Muziek_member[t,p]=1} Muziek_missing[p,w] * Muziek_essential[p]) <= Muziek_maximum_missing[t];
subject to single_Muziek
  {w in weeks}:
  (sum {x in Muziek_teams} Muziek[x,w]) = 1;
subject to ritme_Muziek
  {w1 in weeks_extended, x in Muziek_teams}:
  (sum {w2 in w1..(w1 + Muziek_ritme[x]-1): w2 in weeks} Muziek[x,w2])
    <= 1 + Muziek_offritme[x,w1];
subject to minimum_Muziek
  {x in Muziek_teams}:
  (sum {w in weeks} Muziek[x,w])
    >= number_of_weeks/Muziek_ritme[x]-2;
subject to maximum_Muziek
  {x in Muziek_teams}:
  (sum {w in weeks} Muziek[x,w])
    <= number_of_weeks/Muziek_ritme[x]+2;
subject to rest_Muziek
  {x in Muziek_teams, w1 in weeks}:
  (sum {w2 in w1..(w1 + Muziek_rest[x]): w2 in weeks} Muziek[x,w2])
    <= 1;
subject to available_Koffie
  {w in weeks, t in Koffie_teams, p in Koffie_persons: Koffie_member[t,p]=1 and Koffie_essential[p]=0}:
  Koffie[t,w] <= Koffie_available[p,w] + 0.5 * Koffie_rather_not[p,w];
subject to missing_Koffie
  {w in weeks, t in Koffie_teams, p in Koffie_persons: Koffie_member[t,p]=1 and Koffie_essential[p]>=1}:
  Koffie[t,w] <= Koffie_available[p,w] + Koffie_missing[p,w];
subject to maximum_missing_Koffie
  {w in weeks, t in Koffie_teams}:
  (sum {p in Koffie_persons: Koffie_member[t,p]=1} Koffie_missing[p,w] * Koffie_essential[p]) <= Koffie_maximum_missing[t];
subject to single_Koffie
  {w in weeks}:
  (sum {x in Koffie_teams} Koffie[x,w]) = 1;
subject to ritme_Koffie
  {w1 in weeks_extended, x in Koffie_teams}:
  (sum {w2 in w1..(w1 + Koffie_ritme[x]-1): w2 in weeks} Koffie[x,w2])
    <= 1 + Koffie_offritme[x,w1];
subject to minimum_Koffie
  {x in Koffie_teams}:
  (sum {w in weeks} Koffie[x,w])
    >= number_of_weeks/Koffie_ritme[x]-2;
subject to maximum_Koffie
  {x in Koffie_teams}:
  (sum {w in weeks} Koffie[x,w])
    <= number_of_weeks/Koffie_ritme[x]+2;
subject to rest_Koffie
  {x in Koffie_teams, w1 in weeks}:
  (sum {w2 in w1..(w1 + Koffie_rest[x]): w2 in weeks} Koffie[x,w2])
    <= 1;
subject to available_Leiding_Blauw
  {w in weeks, p in Leiding_Blauw_persons}:
  Leiding_Blauw[p,w] <= Leiding_Blauw_available[p,w] + 0.5 * Leiding_Blauw_rather_not[p,w];
subject to single_Leiding_Blauw
  {w in weeks}:
  (sum {x in Leiding_Blauw_persons} Leiding_Blauw[x,w]) = 1;
subject to ritme_Leiding_Blauw
  {w1 in weeks_extended, x in Leiding_Blauw_persons}:
  (sum {w2 in w1..(w1 + Leiding_Blauw_ritme[x]-1): w2 in weeks} Leiding_Blauw[x,w2])
    <= 1 + Leiding_Blauw_offritme[x,w1];
subject to minimum_Leiding_Blauw
  {x in Leiding_Blauw_persons}:
  (sum {w in weeks} Leiding_Blauw[x,w])
    >= number_of_weeks/Leiding_Blauw_ritme[x]-2;
subject to maximum_Leiding_Blauw
  {x in Leiding_Blauw_persons}:
  (sum {w in weeks} Leiding_Blauw[x,w])
    <= number_of_weeks/Leiding_Blauw_ritme[x]+2;
subject to rest_Leiding_Blauw
  {x in Leiding_Blauw_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Leiding_Blauw_rest[x]): w2 in weeks} Leiding_Blauw[x,w2])
    <= 1;
subject to single_Groep_Blauw
  {w in weeks}:
	(sum {p in Groep_Blauw_persons} Groep_Blauw[p,w]) = 1;
subject to available_Groep_Blauw
  {w in weeks, p in Groep_Blauw_persons}:
  Groep_Blauw[p,w] <= Groep_Blauw_available[p,w];
subject to prefered_pair_Groep_Blauw
  {w in weeks, p1 in Leiding_Blauw_persons, p2 in Groep_Blauw_persons}:
  Leiding_Blauw[p1,w] + Groep_Blauw[p2,w] <= 1 + Groep_Blauw_prefered_pair[p1,p2] + Groep_Blauw_not_prefered_pair[w];
subject to available_Leiding_Wit
  {w in weeks, p in Leiding_Wit_persons}:
  Leiding_Wit[p,w] <= Leiding_Wit_available[p,w] + 0.5 * Leiding_Wit_rather_not[p,w];
subject to single_Leiding_Wit
  {w in weeks}:
  (sum {x in Leiding_Wit_persons} Leiding_Wit[x,w]) = 1;
subject to ritme_Leiding_Wit
  {w1 in weeks_extended, x in Leiding_Wit_persons}:
  (sum {w2 in w1..(w1 + Leiding_Wit_ritme[x]-1): w2 in weeks} Leiding_Wit[x,w2])
    <= 1 + Leiding_Wit_offritme[x,w1];
subject to minimum_Leiding_Wit
  {x in Leiding_Wit_persons}:
  (sum {w in weeks} Leiding_Wit[x,w])
    >= number_of_weeks/Leiding_Wit_ritme[x]-2;
subject to maximum_Leiding_Wit
  {x in Leiding_Wit_persons}:
  (sum {w in weeks} Leiding_Wit[x,w])
    <= number_of_weeks/Leiding_Wit_ritme[x]+2;
subject to rest_Leiding_Wit
  {x in Leiding_Wit_persons, w1 in weeks}:
  (sum {w2 in w1..(w1 + Leiding_Wit_rest[x]): w2 in weeks} Leiding_Wit[x,w2])
    <= 1;
subject to single_Groep_Wit
  {w in weeks}:
	(sum {p in Groep_Wit_persons} Groep_Wit[p,w]) = 1;
subject to available_Groep_Wit
  {w in weeks, p in Groep_Wit_persons}:
  Groep_Wit[p,w] <= Groep_Wit_available[p,w];
subject to prefered_pair_Groep_Wit
  {w in weeks, p1 in Leiding_Wit_persons, p2 in Groep_Wit_persons}:
  Leiding_Wit[p1,w] + Groep_Wit[p2,w] <= 1 + Groep_Wit_prefered_pair[p1,p2] + Groep_Wit_not_prefered_pair[w];
subject to Zangleiding_excludes_Geluid
  {w in weeks, p in Zangleiding_persons inter Geluid_persons}:
  Zangleiding[p,w] + Geluid[p,w] <= 1;
subject to Zangleiding_excludes_Leiding_Rood
  {w in weeks, p in Zangleiding_persons inter Leiding_Rood_persons}:
  Zangleiding[p,w] + Leiding_Rood[p,w] <= 1;
subject to Muziek_excludes_Leiding_Wit
  {w in weeks, p in Muziek_persons inter Leiding_Wit_persons, t in Muziek_teams: Muziek_member[t,p]=1}:
  Muziek[t,w] + Leiding_Wit[p,w] <= 1;
subject to Muziek_excludes_Welkom
  {w in weeks, p in Muziek_persons inter Welkom_persons, t in Muziek_teams: Muziek_member[t,p]=1}:
  Muziek[t,w] + Welkom[p,w] <= 1;
subject to Muziek_excludes_Hulpkoster
  {w in weeks, p in Muziek_persons inter Hulpkoster_persons, t in Muziek_teams: Muziek_member[t,p]=1}:
  Muziek[t,w] + Hulpkoster[p,w] <= 1;
subject to Beamer_excludes_Geluid
  {w in weeks, p in Beamer_persons inter Geluid_persons}:
  Beamer[p,w] + Geluid[p,w] <= 1;
subject to Muziek_excludes_Beamer
  {w in weeks, p in Muziek_persons inter Beamer_persons, t in Muziek_teams: Muziek_member[t,p]=1}:
  Muziek[t,w] + Beamer[p,w] <= 1;
subject to Groep_Blauw_excludes_Beamer
  {w in weeks, p in Groep_Blauw_persons inter Beamer_persons}:
  Groep_Blauw[p,w] + Beamer[p,w] <= 1;
subject to Groep_Wit_excludes_Beamer
  {w in weeks, p in Groep_Wit_persons inter Beamer_persons}:
  Groep_Wit[p,w] + Beamer[p,w] <= 1;
subject to Groep_Blauw_excludes_Geluid
  {w in weeks, p in Groep_Blauw_persons inter Geluid_persons}:
  Groep_Blauw[p,w] + Geluid[p,w] <= 1;
subject to Geluid_excludes_Hoofdkoster
  {w in weeks, p in Geluid_persons inter Hoofdkoster_persons}:
  Geluid[p,w] + Hoofdkoster[p,w] <= 1;
subject to Geluid_excludes_Hulpkoster
  {w in weeks, p in Geluid_persons inter Hulpkoster_persons}:
  Geluid[p,w] + Hulpkoster[p,w] <= 1;
subject to Groep_Blauw_excludes_Groep_Wit
  {w in weeks, p in Groep_Blauw_persons inter Groep_Wit_persons}:
  Groep_Blauw[p,w] + Groep_Wit[p,w] <= 1;
subject to Koffie_excludes_Leiding_Blauw
  {w in weeks, p in Koffie_persons inter Leiding_Blauw_persons, t in Koffie_teams: Koffie_member[t,p]=1}:
  Koffie[t,w] + Leiding_Blauw[p,w] <= 1;
subject to Welkom_excludes_Leiding_Blauw
  {w in weeks, p in Welkom_persons inter Leiding_Blauw_persons}:
  Welkom[p,w] + Leiding_Blauw[p,w] <= 1;
subject to Welkom_excludes_Leiding_Wit
  {w in weeks, p in Welkom_persons inter Leiding_Wit_persons}:
  Welkom[p,w] + Leiding_Wit[p,w] <= 1;
subject to Welkom_excludes_Leiding_Rood
  {w in weeks, p in Welkom_persons inter Leiding_Rood_persons}:
  Welkom[p,w] + Leiding_Rood[p,w] <= 1;
subject to Koffie_excludes_Leiding_Rood
  {w in weeks, p in Koffie_persons inter Leiding_Rood_persons, t in Koffie_teams: Koffie_member[t,p]=1}:
  Koffie[t,w] + Leiding_Rood[p,w] <= 1;
subject to Leiding_Rood_excludes_Hulpkoster
  {w in weeks, p in Leiding_Rood_persons inter Hulpkoster_persons}:
  Leiding_Rood[p,w] + Hulpkoster[p,w] <= 1;
subject to Hulpkoster_excludes_Beamer
  {w in weeks, p in Hulpkoster_persons inter Beamer_persons}:
  Hulpkoster[p,w] + Beamer[p,w] <= 1;

# extra start
subject to een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_zn_eigen_team
    {p in Zangleiding_persons inter Muziek_teams, w in weeks}:
    Muziek[p,w] >= Zangleiding[p,w];

subject to rijswijk_special1
    {w in weeks}:
    Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne;

subject to rijswijk_special2
    {w in weeks}:
    Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs;

subject to wijngaarden_special
    {w in weeks}: Leiding_Blauw['Rachel',w] + Leiding_Rood['Tim',w] = 2 * timofrachel[w] - wijngaardenbreuk[w];
# extra end

solve;
display {w in weeks, Zangleiding_ in Zangleiding_persons: Zangleiding[Zangleiding_,w]=1}: w, Zangleiding_;
display {w in weeks, rather_not_ in Zangleiding_persons: Zangleiding_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Geluid_ in Geluid_persons: Geluid[Geluid_,w]=1}: w, Geluid_;
display {w in weeks, rather_not_ in Geluid_persons: Geluid_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Beamer_ in Beamer_persons: Beamer[Beamer_,w]=1}: w, Beamer_;
display {w in weeks, rather_not_ in Beamer_persons: Beamer_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Leiding_Rood_ in Leiding_Rood_persons: Leiding_Rood[Leiding_Rood_,w]=1}: w, Leiding_Rood_;
display {w in weeks, rather_not_ in Leiding_Rood_persons: Leiding_Rood_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Welkom_ in Welkom_persons: Welkom[Welkom_,w]=1}: w, Welkom_;
display {w in weeks, rather_not_ in Welkom_persons: Welkom_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Hoofdkoster_ in Hoofdkoster_persons: Hoofdkoster[Hoofdkoster_,w]=1}: w, Hoofdkoster_;
display {w in weeks, rather_not_ in Hoofdkoster_persons: Hoofdkoster_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Hulpkoster_ in Hulpkoster_persons: Hulpkoster[Hulpkoster_,w]=1}: w, Hulpkoster_;
display {w in weeks, rather_not_ in Hulpkoster_persons: Hulpkoster_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, missing_ in Muziek_persons: Muziek_missing[missing_,w]=1}: w, missing_;
display {w in weeks, Muziek_ in Muziek_teams: Muziek[Muziek_,w]=1}: w, Muziek_;
display {w in weeks, rather_not_ in Muziek_persons: Muziek_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, missing_ in Koffie_persons: Koffie_missing[missing_,w]=1}: w, missing_;
display {w in weeks, Koffie_ in Koffie_teams: Koffie[Koffie_,w]=1}: w, Koffie_;
display {w in weeks, rather_not_ in Koffie_persons: Koffie_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Leiding_Blauw_ in Leiding_Blauw_persons: Leiding_Blauw[Leiding_Blauw_,w]=1}: w, Leiding_Blauw_;
display {w in weeks, rather_not_ in Leiding_Blauw_persons: Leiding_Blauw_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, not_prefered_pair_ in Groep_Blauw_persons: Groep_Blauw_not_prefered_pair[w]=1 and Groep_Blauw[not_prefered_pair_,w]=1}: w, not_prefered_pair_;
display {w in weeks, Groep_Blauw_ in Groep_Blauw_persons: Groep_Blauw[Groep_Blauw_,w]=1}: w, Groep_Blauw_;
display {w in weeks, rather_not_ in Groep_Blauw_persons: Groep_Blauw_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, Leiding_Wit_ in Leiding_Wit_persons: Leiding_Wit[Leiding_Wit_,w]=1}: w, Leiding_Wit_;
display {w in weeks, rather_not_ in Leiding_Wit_persons: Leiding_Wit_rather_not[rather_not_,w]=1}: w, rather_not_;
display {w in weeks, not_prefered_pair_ in Groep_Wit_persons: Groep_Wit_not_prefered_pair[w]=1 and Groep_Wit[not_prefered_pair_,w]=1}: w, not_prefered_pair_;
display {w in weeks, Groep_Wit_ in Groep_Wit_persons: Groep_Wit[Groep_Wit_,w]=1}: w, Groep_Wit_;
display {w in weeks, rather_not_ in Groep_Wit_persons: Groep_Wit_rather_not[rather_not_,w]=1}: w, rather_not_;
end;
