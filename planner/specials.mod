var wijngaardenbreuk {weeks}, binary;
var matthijszonderlianne, binary;
var liannezondermatthijs, binary;
var geenrustjolanda {weeks}, binary;

+ (sum {w in weeks} 8 * wijngaardenbreuk[w])
+ 10 * matthijszonderlianne
+ 20 * liannezondermatthijs
+ (sum {w in weeks} 8 * geenrustjolanda[w])

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

subject to Als_Matthuis_hoofdkoster_is_doet_Lianne_welkom
    {w in weeks}:
    Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne;

subject to Als_Lianne_welkom_doet_is_Matthijs_hoofdkoster
    {w in weeks}:
    Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs;

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