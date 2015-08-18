var wijngaardenbreuk {weeks}, binary;
#var matthijszonderlianne, binary;
#var liannezondermatthijs, binary;
var geenrustjolanda {weeks}, binary;

+ (sum {w in weeks} 8 * wijngaardenbreuk[w])
#+ 10 * matthijszonderlianne
#+ 20 * liannezondermatthijs
+ (sum {w in weeks} 8 * geenrustjolanda[w])

#ignore minimum_Beamer
#ignore maximum_Beamer
#ignore rest_Beamer
#ignore minimum_Leiding_Blauw
#ignore maximum_Leiding_Blauw
#ignore rest_Leiding_Blauw
#ignore rest_Groep_Blauw
#ignore minimum_Geluid
#ignore maximum_Geluid
#ignore rest_Geluid
#ignore minimum_Hoofdkoster
#ignore maximum_Hoofdkoster
#ignore rest_Hoofdkoster
#ignore minimum_Hulpkoster
#ignore maximum_Hulpkoster
#ignore rest_Hulpkoster
#ignore minimum_Koffie
#ignore maximum_Koffie
#ignore rest_Koffie
#ignore minimum_Muziek
#ignore maximum_Muziek
#ignore rest_Muziek
#ignore minimum_Leiding_Rood
#ignore maximum_Leiding_Rood
#ignore rest_Leiding_Rood
#ignore rest_Groep_Rood
ignore minimum_Welkom
ignore maximum_Welkom
ignore rest_Welkom
ignore minimum_Leiding_Wit
ignore maximum_Leiding_Wit
ignore rest_Leiding_Wit
#ignore rest_Groep_Wit
#ignore minimum_Zangleiding
#ignore maximum_Zangleiding
#ignore rest_Zangleiding

subject to Een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_eigen_team
    {p in Zangleiding_persons inter Muziek_teams, w in weeks}:
    Muziek[p,w] >= Zangleiding[p,w];

subject to Jolanda_heeft_1_week_rust_tussen_zangleiding_en_leiding_van_groep_Rood
    {w in first_week..(last_week-1)}:
    Zangleiding['Jolanda',w] + Leiding_Rood['Jolanda',w+1] <= 1 + geenrustjolanda[w];

subject to Jolanda_heeft_1_week_rust_tussen_leiding_van_groep_Rood_en_zangleiding
    {w in first_week..(last_week-1)}:
    Leiding_Rood['Jolanda',w] + Zangleiding['Jolanda',w+1] <= 1 + geenrustjolanda[w];

subject to Jolanda_geen_zangleiding_tegelijkertijd_met_Wim_A_hulpkoster
    {w in weeks}:
    Zangleiding['Jolanda',w] + Hulpkoster['Wim_A',w] <= 1;

#subject to Als_Matthuis_hoofdkoster_is_doet_Lianne_welkom
#    {w in weeks}:
#    Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne;

#subject to Als_Lianne_welkom_doet_is_Matthijs_hoofdkoster
#    {w in weeks}:
#    Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs;

subject to Rachel_leidt_groep_Blauw_wanneer_Tim_groep_Rood_leidt
    {w in weeks}:
    Leiding_Rood['Tim',w] <= Leiding_Blauw['Rachel',w] + wijngaardenbreuk[w];

subject to Tim_leidt_groep_Rood_wanneer_Rachel_groep_Blauw_leidt
    {w in weeks}:
    Leiding_Blauw['Rachel',w] <= Leiding_Rood['Tim',w] + wijngaardenbreuk[w];

subject to Yentl_doet_de_leiding_van_groep_Wit_en_Rood_tegelijkertijd
    {w in weeks}:
    Leiding_Rood['Yentl',w] = Leiding_Wit['Yentl',w];

subject to Justin_mag_niet_missen_als_Joshua_en_Inge_de_zangleiding_hebben
  {w in weeks}:
  Muziek_missing['Justin',w] + Zangleiding['Inge',w] <= 1;

subject to Justin_heeft_minimaal_3_weken_rust_tussen_muziekbeurten
  {w1 in weeks}:
  (sum {w2 in w1..(w1+3): w2 in weeks} (Muziek['Inge',w2] - Muziek_missing['Justin',w2])) <= 1;

subject to Justin_heeft_minimaal_3_weken_rust_tussen_muziekbeurten_historisch
  {w in (Muziek_last['Inge']+1)..(Muziek_last['Inge']+3): w in weeks}:
  Muziek['Inge',w] - Muziek_missing['Justin',w] = 0;