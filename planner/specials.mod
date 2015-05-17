var timofrachel {weeks}, binary;
var wijngaardenbreuk {weeks}, binary;
var matthijszonderlianne, binary;
var liannezondermatthijs, binary;
var geenrustjolanda {weeks}, binary;

+ (sum {w in weeks} 4 * wijngaardenbreuk[w])
+ 10*matthijszonderlianne + 20*liannezondermatthijs
+ (sum {w in weeks} 8 * geenrustjolanda[w])

#subject to ritme_Hoofdkoster
#  {w1 in weeks_extended, x in Hoofdkoster_persons}:
#  (sum {w2 in w1..(w1 + Hoofdkoster_ritme[x]-1): w2 in weeks} Hoofdkoster[x,w2])
#    <= 2 + Hoofdkoster_offritme[x,w1]; # 2 ipv 1
#
#subject to dubbele_diensten_Hoofdkoster
#    {p in Hoofdkoster_persons, w in 0..(number_of_weeks/2-1): (first_week+2*w+1) in weeks}:
#    Hoofdkoster[p,first_week+2*w] = Hoofdkoster[p,first_week+2*w+1]; # extra regel
#
#subject to rest_Hoofdkoster
#  {x in Hoofdkoster_persons, w1 in weeks}:
#  (sum {w2 in w1..(w1 + Hoofdkoster_rest[x] + 1): w2 in weeks} Hoofdkoster[x,w2])
#    <= 2;

subject to een_zangleider_die_ook_in_een_muziekteam_zit_leidt_de_dienst_alleen_met_zn_eigen_team
    {p in Zangleiding_persons inter Muziek_teams, w in weeks}:
    Muziek[p,w] >= Zangleiding[p,w];

subject to Jolanda_1_week_rust_tussen_rood_en_zangleiding
    {w in first_week..(last_week-1)}:
    Zangleiding['Jolanda',w] + Leiding_Rood['Jolanda',w+1] <= 1 + geenrustjolanda[w];

subject to Jolanda_1_week_rust_tussen_zangleiding_en_rood
    {w in first_week..(last_week-1)}:
    Leiding_Rood['Jolanda',w] + Zangleiding['Jolanda',w+1] <= 1 + geenrustjolanda[w];

subject to rijswijk_special1
    {w in weeks}:
    Hoofdkoster['Matthijs',w] <= Welkom['Lianne',w] + matthijszonderlianne;

subject to rijswijk_special2
    {w in weeks}:
    Welkom['Lianne',w] <= Hoofdkoster['Matthijs',w] + liannezondermatthijs;

subject to wijngaarden_special
    {w in weeks}: Leiding_Blauw['Rachel',w] + Leiding_Rood['Tim',w] = 2 * timofrachel[w] - wijngaardenbreuk[w];

subject to jacolien_na_vakantie_wit
    {w in weeks: w < 34}:
    Leiding_Wit['Jacolien',w] = 0;
    
subject to yentl_na_vakantie_rood
    {w in weeks: w < 34}:
    Leiding_Rood['Yentl',w] = 0;
    
subject to yentl_green_vredesdienst:
    Leiding_Rood['Yentl',38] = 0;
    
subject to witrood_combi
    {w in weeks: w >= 34}:
    Leiding_Rood['Yentl',w] = Leiding_Wit['Yentl',w];
