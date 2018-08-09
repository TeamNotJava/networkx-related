# see sage worksheet "eval-notebook.ipynb"
planar_graph_evals = dict()
planar_graph_evals[100] = {
    'D(x*G_1_dx(x,y),y)': 1.09347848647472549211184239941769601061,
    'D_dx(x*G_1_dx(x,y),y)': 3.45102206434801157864803811245239712851,
    'G_1(x,y)': 0.0372484305053690456202661877963311349072,
    'G_1_dx(x,y)': 1.03960692373287371278312170556092216601,
    'G_1_dx_dx(x,y)': 1.1831386535487874823112196643179832576,
    'G_2_dx(x*G_1_dx(x,y),y)': 0.038842683760013258631145523348425252874,
    'G_2_dx_dx(x*G_1_dx(x,y),y)': 1.05099440303963997980334319688998807042,
    'G_3_arrow_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.0182698213762051362133391897289610870537,
    'H(x*G_1_dx(x,y),y)': 0.00206469524549284585247141356302904687086,
    'H_dx(x*G_1_dx(x,y),y)': 0.276441303522129889594403984833856178203,
    'J_a(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.00103234762274642,
    'J_a_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.106695873420575,
    'K(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.21219385343653063,
    'K_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 15.48657625114519,
    'P(x*G_1_dx(x,y),y)': 0.0477986369539869322752735578478273809975,
    'P_dx(x*G_1_dx(x,y),y)': 1.80255895061461154228734452882283065547,
    'R_b(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.5120292887029289,
    'R_w(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 2.577655310621243,
    'S(x*G_1_dx(x,y),y)': 0.0436151542752457139840974280068395827400,
    'S_dx(x*G_1_dx(x,y),y)': 1.37202181021127014676628959879571029484,
    'x': 0.0365447705189290291920092340981152311040,
    'x*G_1_dx(x,y)': 0.0379921964577076229466965829549486315897,
    'y': 1.00000000000000
}

planar_graph_evals_n1000_mu2 = {
    'D(x*G_1_dx(x,y),y)': 0.637806651054576543789868114281052782226,
    'D_dx(x*G_1_dx(x,y),y)': 0.696569004272650034553258501901187844797,
    'G_1(x,y)': 0.0371350974110612431577106176437625479004,
    'G_1_dx(x,y)': 1.02349152146425090041372148084962313028,
    'G_1_dx_dx(x,y)': 0.6681252576686826620451319953849912978,
    'G_2_dx(x*G_1_dx(x,y),y)': 0.023219842219972369437856348855081731951,
    'G_2_dx_dx(x*G_1_dx(x,y),y)': 0.622880478267134011353588999105453800863,
    'G_3_arrow_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.000679173063574668255997920599118410526120,
    'H(x*G_1_dx(x,y),y)': 0.0000823773831520415917684978054015601056388,
    'H_dx(x*G_1_dx(x,y),y)': 0.00510427337050757305444031263634611369205,
    'J_a(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.0000411886915760208,
    'J_a_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.00231559123294228,
    'K(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.011409175629378519,
    'K_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.3411352773706396,
    'P(x*G_1_dx(x,y),y)': 0.00938930779484682350336768502426592529014,
    'P_dx(x*G_1_dx(x,y),y)': 0.271262998936713526179079307546743223900,
    'R_b(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.04589839549189142,
    'R_w(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.4674525884161968,
    'S(x*G_1_dx(x,y),y)': 0.0149266596473254870549308539222398010276,
    'S_dx(x*G_1_dx(x,y),y)': 0.420201731965428935319738881718098507204,
    'x': 0.0367100483755473011833298788754433904407,
    'x*G_1_dx(x,y)': 0.0375724232649151595081505057178980179655,
    'y': 0.61340830622925219163980107752914549580
}

planar_graph_evals[1000] = {
    'D(x*G_1_dx(x,y),y)': 1.09410365137374004442949439446589198249,
    'D_dx(x*G_1_dx(x,y),y)': 3.55196572933420691992480228903908993177,
    'G_1(x,y)': 0.0374202706756538898981827103195911450645,
    'G_1_dx(x,y)': 1.03980258991076744240676377873318958256,
    'G_1_dx_dx(x,y)': 1.1846774415112270278413185976194078480,
    'G_2_dx(x*G_1_dx(x,y),y)': 0.039030877742186944047923311524402278009,
    'G_2_dx_dx(x*G_1_dx(x,y),y)': 1.05172845812047078798847446437969622346,
    'G_3_arrow_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.0206691134547898290979819665022118221479,
    'H(x*G_1_dx(x,y),y)': 0.00211690236570744191405430580782101425957,
    'H_dx(x*G_1_dx(x,y),y)': 0.314085143613958191927506186335308955728,
    'J_a(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.00105845118285372,
    'J_a_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.120334580483412,
    'K(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.21625622410465262,
    'K_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 17.687860689552128,
    'P(x*G_1_dx(x,y),y)': 0.0481252214870148144168050624406156526488,
    'P_dx(x*G_1_dx(x,y),y)': 1.85579098315862781296255814730413923967,
    'R_b(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.5593091186182373,
    'R_w(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 2.733773804897007,
    'S(x*G_1_dx(x,y),y)': 0.0438615275210177880986350262174553155774,
    'S_dx(x*G_1_dx(x,y),y)': 1.38208960256162091503473795539964173636,
    'x': 0.0367100483755473011833298788754433904407,
    'x*G_1_dx(x,y)': 0.0381712033766436449320149605392031808199,
    'y': 1.00000000000000
}

# N = 100
reference_evals = {
    'D(x*G_1_dx(x,y),y)': 1.09347848647472549211184239941769601061,
    'D_dx(x*G_1_dx(x,y),y)': 3.45102206434801157864803811245239712851,

    #'Fusy_K': 0.00206469524549284585247141356302904687086,
    'G_3_arrow(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.00206469524549284585247141356302904687086,

    'Fusy_K_dx': 0.213391746841149010553294208298541737991,
    'Fusy_K_dy': 0.0182698213762051362133391897289610870537,
    'G_1(x,y)': 0.0372484305053690456202661877963311349072,
    'G_1_dx(x,y)': 1.03960692373287371278312170556092216601,
    'G_1_dx_dx(x,y)': 1.1831386535487874823112196643179832576,
    'G_2_dx(x*G_1_dx(x,y),y)': 0.038842683760013258631145523348425252874,
    'G_2_dx_dx(x*G_1_dx(x,y),y)': 1.05099440303963997980334319688998807042,
    'G_3_arrow_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.0182698213762051362133391897289610870537,
    'H(x*G_1_dx(x,y),y)': 0.00206469524549284585247141356302904687086,
    'H_dx(x*G_1_dx(x,y),y)': 0.276441303522129889594403984833856178203,
    'J_a(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.00103234762274642,
    'J_a_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.106695873420575,
    'K(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.21219385343653063,
    'K_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 15.48657625114519,
    'K_dx_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 5592.386366298111,
    'K_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1.729773462783172,
    'K_dy_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 539.8558558558559,
    'K_dy_dx_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1183895.1899970463,
    'K_snake(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1.254888507718696,
    'K_snake_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 543.8610354223433,
    'K_snake_dx_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1277786.7614037835,
    'P(x*G_1_dx(x,y),y)': 0.0477986369539869322752735578478273809975,
    'P_dx(x*G_1_dx(x,y),y)': 1.80255895061461154228734452882283065547,
    'R_b(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.5120292887029289,
    'R_b_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 129.2273161413563,
    'R_w(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 2.577655310621243,
    'R_w_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 414.9509202453988,
    'S(x*G_1_dx(x,y),y)': 0.0436151542752457139840974280068395827400,
    'S_dx(x*G_1_dx(x,y),y)': 1.37202181021127014676628959879571029484,
    'x': 0.0365447705189290291920092340981152311040,
    'x*G_1_dx(x,y)': 0.0379921964577076229466965829549486315897,
    'y': 1.00000000000000}

planar_graph_evals[10000] = {
  'D(x*G_1_dx(x,y),y)': 1.09416749105326839436361139331519184699,
  'D_dx(x*G_1_dx(x,y),y)': 3.58480499936306184450275887839568999541,
  'D_dx_dx(x*G_1_dx(x,y),y)': 3844.44528283854975380346115822251416046,
  'Fusy_K': 0.00212262026119702814886982142258999866449,
  'Fusy_K_dx': 0.249953080767411054035497390586634583600,
  'Fusy_K_dx_dx': 840.103572875302590376914748297187794199,
  'Fusy_K_dy': 0.0214683058020723592469997145512349623450,
  'Fusy_K_dy_dy': 6.12142458745962758412596335033700990508,
  'Fusy_k_dx_dy': 72.0981198866882684638807996945396894562,
  'G(x,y)': 1.03814706567105803659247685817331208031,
  'G_1(x,y)': 0.0374374564718087765508715224183234143412,
  'G_1_dx(x,y)': 1.03982217197897390330627046797765213524,
  'G_1_dx_dx(x,y)': 1.1849448423679601844906264429882820439,
  'G_1_dx_dx_dx(x,y)': 26.97717307615521913829963604535756800,
  'G_2_dx(x*G_1_dx(x,y),y)': 0.039049710051328373527902391160990973285,
  'G_2_dx_dx(x*G_1_dx(x,y),y)': 1.05189847611928530057997563610421892748,
  'G_2_dx_dx_dx(x*G_1_dx(x,y),y)': 17.9872451737400462981579319960233386141,
  'G_3_arrow_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.0214683058020723592469997145512349623450,
  'G_dx(x,y)': 1.07948833665967802456253351678818766059,
  'G_dx_dx(x,y)': 2.35262291793778847713055101300644029098,
  'G_dx_dx_dx(x,y)': 33.0108508153309009525655605898420142252,
  'H(x*G_1_dx(x,y),y)': 0.00212262026119702814886982142258999866449,
  'H_dx(x*G_1_dx(x,y),y)': 0.326912770734535074726715514177226469305,
  'H_dx_dx(x*G_1_dx(x,y),y)': 1518.21806872915956879873505899143586685,
  'J_a(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.00106131013059851,
  'J_a_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.124976540383706,
  'K(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.21670360435516503,
  'K_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 18.462984966367003,
  'K_dx_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 70657.42195884386,
  'K_dy(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1.998149518874907,
  'K_dy_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 6094.863636363636,
  'K_dy_dx_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1189664441.662329,
  'K_snake(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1.536199432751157,
  'K_snake_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 6613.412698412699,
  'K_snake_dx_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1301480185.0630813,
  'P(x*G_1_dx(x,y),y)': 0.0481585761872462889748092768486110858080,
  'P_dx(x*G_1_dx(x,y),y)': 1.87300065960603866766879075789499635792,
  'P_dx_dx(x*G_1_dx(x,y),y)': 2011.58863957504105608992077970919220810,
  'R_b(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 0.5749385151094553,
  'R_b_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 1405.924242424242,
  'R_w(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 2.78591483387927,
  'R_w_dx(x*G_1_dx(x,y),D(x*G_1_dx(x,y),y))': 4693.272727272727,
  'S(x*G_1_dx(x,y),y)': 0.0438862946048250772399322950439907625167,
  'S_dx(x*G_1_dx(x,y),y)': 1.38489156902248810210725260632346716819,
  'S_dx_dx(x*G_1_dx(x,y),y)': 314.638574534349128914805319521886085503,
  'x': 0.0367265761612091283824619433531762063743,
  'x*G_1_dx(x,y)': 0.0381891081932996814792832195422959507297,
  'y': 1.00000000000000}

all_evaluations = [
    reference_evals,
    # planar_graph_evals_n100,
    # planar_graph_evals_n1000
    # planar_graph_evals_n10000
]
