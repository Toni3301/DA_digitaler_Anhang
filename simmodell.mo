within DA_Antonia;
model simmodell
  extends Modelica.Icons.Example;
  package Medium_Water = AixLib.Media.Water "Medium model";
  package Medium_sou = AixLib.Media.Air annotation (__Dymola_choicesAllMatching =     true);
  parameter Modelica.Units.SI.PressureDifference dp_nom(displayUnit="Pa") = 500
    "nominal pressure difference for all components"                                                                                       annotation (Dialog(group=
          "Hydraulik"));
  parameter Modelica.Units.SI.MassFlowRate mp_nom=0.18    "nominal mass flow rate for all components"    annotation (Dialog(group="Hydraulik"));
  parameter Modelica.Units.SI.MassFlowRate mp_nom_sou=2    "Nennmassestrom Quellkreis Wärmepumpe"    annotation (Dialog(group="Hydraulik"));
  parameter Modelica.Units.SI.Pressure dp_nom_sou=10    "Pressure difference Quellkreis" annotation (Dialog(group="Hydraulik"));
  parameter Integer n_WP_VL=10 "load_VL (number storage layer)"    annotation (Dialog(group="Verrohrung"));
  parameter Integer n_WP_RL=21 "load_VL (number storage layer)"    annotation (Dialog(group="Verrohrung"));
  parameter Real f_WP_min=0.3 "minimale Teillast der Wärmepumpe"    annotation (Dialog(tab="Regelung", group="Wärmepumpe"));
  inner Modelica.Fluid.System system
    annotation (Placement(transformation(extent={{206,116},{226,136}})));
  Buildings.BoundaryConditions.WeatherData.ReaderTMY3 B_weaDat(filNam=weaFil,
      computeWetBulbTemperature=false)
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},
        rotation=0,
        origin={224,62})));
  Modelica.Units.SI.Angle lat =      Buildings.BoundaryConditions.WeatherData.BaseClasses.getLatitudeTMY3(      weaFil) "Latitude";
  LibEAS.HeatingCircuits.HeatedRooms.MBL.Room_Radiator_Control B_EG(
    nConExt=0,
    nConExtWin=3,
    nConPar=0,
    nConBou=2,
    nSurBou=1,
    redeclare package Medium_Water = Medium_Water,
    dp_nom_rad=10*dp_nom,
    kv_valve=1,
    AFlo=72,
    hRoo=3,
    T_Set=294.65,
    Qp_HK_nom=4250,
    eHyst=1,
    k_PI=1,
    Ti_PI=2000,
    datConExtWin(
      layers={db.AW,db.AW,db.AW},
      A={24,27,24},
      glaSys={db.Fenster,db.Fenster,db.Fenster},
      each wWin=1.0,
      each hWin=1.0,
      each fFra=0.1,
      til={Buildings.Types.Tilt.Wall,Buildings.Types.Tilt.Wall,Buildings.Types.Tilt.Wall},
      azi={Buildings.Types.Azimuth.S,Buildings.Types.Azimuth.E,Buildings.Types.Azimuth.N}),
    surBou(A={72}, til={Buildings.Types.Tilt.Ceiling}),
    datConBou(
      layers={db.Bodenplatte_ged,db.ZW},
      A={72,27},
      til={Buildings.Types.Tilt.Floor,Buildings.Types.Tilt.Wall},
      azi={Buildings.Types.Azimuth.N,Buildings.Types.Azimuth.W}),
    room_load(mixedAir(
        intConMod=Buildings.HeatTransfer.Types.InteriorConvection.Fixed,
        hIntFixed=3,
        extConMod=Buildings.HeatTransfer.Types.ExteriorConvection.Fixed,
        hExtFixed=10)))                                           "EG"
    annotation (Placement(transformation(rotation=0, extent={{258,-14},{278,6}})));
  LibEAS.Sensors.TemperatureTwoPort_Display WP_senT_VL(redeclare package Medium
      = Medium_Water, m_flow_nominal=mp_nom)
    annotation (Placement(transformation(extent={{-44,2},{-24,22}})));
  LibEAS.Sensors.PressureDrop_Display WP_dp_VL(
    redeclare package Medium = Medium_Water,
    m_flow_nominal=mp_nom,
    dp_nominal=6600)
    annotation (Placement(transformation(extent={{-20,2},{0,22}})));
  AixLib.Fluid.Sources.Boundary_pT KK_sou(
    use_T_in=true,
    redeclare package Medium = Medium_sou,
    p=100000,
    T=283.15,
    nPorts=1) "Fluid source on source side"
    annotation (Placement(transformation(extent={{-138,-50},{-118,-30}})));
  AixLib.Fluid.Sources.Boundary_pT KK_sin(
    nPorts=1,
    redeclare package Medium = Medium_sou,
    p=100000,
    T=281.15) "Fluid sink on source side"
    annotation (Placement(transformation(extent={{-138,2},{-118,22}})));
  AixLib.Fluid.Movers.FlowControlled_m_flow WP_pum_RL_sou(
    redeclare package Medium = Medium_sou,
    m_flow_nominal=mp_nom_sou,
    per(
      pressure(V_flow={8.79043600562e-06*100,0.00277777777778*100,0.00556874120956
            *100,0.00776635021097*100,0.00978815049226*100,0.0113484528833*100,0.0127329465541
            *100,0.013985583685*100,0.0154360056259*100}, dp={60,50,49,48,47,46,
            45,44,43}),
      use_powerCharacteristic=true,
      power(V_flow={8.79043600562e-06*100,0.00277777777778*100,0.00556874120956*
            100,0.00776635021097*100,0.00978815049226*100,0.0113484528833*100,0.0127329465541
            *100,0.013985583685*100,0.0154360056259*100}, P={50,60,59,58,57,56,55,
            54,53})),
    final inputType=AixLib.Fluid.Types.InputType.Continuous)
    "Ventilator Wärmepumpe" annotation (Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={-106,-40})));
  LibEAS.Sensors.TemperatureTwoPort_Display WP_senT_VL_sou(redeclare package
      Medium = Medium_sou, m_flow_nominal=mp_nom_sou)
    annotation (Placement(transformation(extent={{-66,2},{-86,22}})));
  LibEAS.Sensors.TemperatureTwoPort_Display WP_senT_RL_sou(redeclare package
      Medium = Medium_sou, m_flow_nominal=mp_nom_sou)
    annotation (Placement(transformation(extent={{10,10},{-10,-10}},
        rotation=180,
        origin={-76,-40})));
  LibEAS.Sensors.PressureDrop_Display WP_dp_VL_sou(
    redeclare package Medium = Medium_sou,
    m_flow_nominal=mp_nom_sou,
    dp_nominal=dp_nom_sou)
    annotation (Placement(transformation(extent={{-94,2},{-114,22}})));
  Modelica.Blocks.Sources.RealExpression re_mp_sou_set(y=2)
    annotation (Placement(transformation(extent={{-124,-24},{-110,-8}})));
  Buildings.Fluid.Sensors.EnthalpyFlowRate WP_senH(redeclare package Medium =
        Medium_Water, m_flow_nominal=mp_nom) annotation (Placement(
        transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={44,-40})));
  LibEAS.Sensors.WMZ WP_senQ(redeclare package Medium = Medium_Water,
      m_flow_nominal=mp_nom)
    annotation (Placement(transformation(extent={{34,2},{54,22}})));
  AixLib.Controls.Interfaces.VapourCompressionMachineControlBus sigBus
    annotation (Placement(transformation(extent={{-66,22},{-46,42}}),
        iconTransformation(extent={{-100,80},{-80,100}})));
  Buildings.BoundaryConditions.WeatherData.Bus
      weaBus "Weather data bus" annotation (Placement(transformation(extent={{-162,
            -46},{-142,-26}}),   iconTransformation(extent={{190,-10},{210,10}})));
  LibEAS.Data.constructions db(KS_175(x=0.01))
    annotation (Placement(transformation(extent={{258,118},{278,138}})));
  Buildings.ThermalZones.Detailed.Constructions.Construction B_SOIL(
    layers=db.Erdreich,
    A=72,
    til=Buildings.Types.Tilt.Floor,
    steadyStateInitial=false,
    T_a_start=282.15,
    T_b_start=282.15) "Erdreich" annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={276,-46})));
  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature B_T_soil_deep(T=282.15)
    "Jahresmitteltemperatur des Erdreichs" annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={270,-88})));
  FMI4BIM.Demonstratoren.Townhouse.Version_2021.zones zd
    annotation (Placement(transformation(extent={{234,118},{254,138}})));
  AixLib.Fluid.Actuators.Valves.ThreeWayLinear V_dwv(
    redeclare package Medium = Medium_Water,
    m_flow_nominal=mp_nom,
    dpValve_nominal=10*dp_nom) annotation (Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={18,12})));
  AixLib.Fluid.FixedResistances.Junction V_jun_RL_1(
    redeclare package Medium = Medium_Water,
    m_flow_nominal={mp_nom,mp_nom,mp_nom},
    dp_nominal={dp_nom,dp_nom,dp_nom}) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=180,
        origin={18,-40})));
  AixLib.Fluid.Movers.FlowControlled_dp     V_pum_VL(
    redeclare package Medium = Medium_Water,
    m_flow_nominal=mp_nom,
    per(
      pressure(V_flow={8.79043600562e-06*100,0.00277777777778*100,0.00556874120956
            *100,0.00776635021097*100,0.00978815049226*100,0.0113484528833*100,0.0127329465541
            *100,0.013985583685*100,0.0154360056259*100}, dp={60,50,49,48,47,46,
            45,44,43}),
      use_powerCharacteristic=true,
      power(V_flow={8.79043600562e-06*100,0.00277777777778*100,0.00556874120956*
            100,0.00776635021097*100,0.00978815049226*100,0.0113484528833*100,0.0127329465541
            *100,0.013985583685*100,0.0154360056259*100}, P={50,60,59,58,57,56,55,
            54,53})),
    final inputType=AixLib.Fluid.Types.InputType.Continuous,
    dp_nominal=dp_nom)                                       annotation (
      Placement(transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={68,12})));
  Modelica.Blocks.Sources.RealExpression V_nSet_pum_VL(y=61000)
                                                              annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={54,32})));
  AixLib.Fluid.Sources.Boundary_pT VS_sin_VL(
    redeclare package Medium = Medium_Water,
    p=150*dp_nom,
    nPorts=1)
    annotation (Placement(transformation(extent={{-10,-10},{10,10}},
        rotation=180,
        origin={118,12})));
  LibEAS.Sensors.TemperatureTwoPort_Display VS_senT_VL(redeclare package Medium
      = Medium_Water, m_flow_nominal=mp_nom) annotation (Placement(
        transformation(
        extent={{10,10},{-10,-10}},
        rotation=180,
        origin={94,12})));
  AixLib.Fluid.Sources.MassFlowSource_T boundary(
redeclare package Medium = Medium_Water,
    use_m_flow_in=true,
    use_T_in=true,
    nPorts=1)
    annotation (Placement(transformation(extent={{166,14},{186,-6}})));
  AixLib.Fluid.Sources.Boundary_pT B_sin(
    redeclare package Medium = Medium_Water,
    p=100000,
    nPorts=1) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=90,
        origin={230,-90})));
  AixLib.Fluid.Sources.MassFlowSource_T boundary1(
    redeclare package Medium = Medium_Water,
    use_m_flow_in=true,
    use_T_in=true,
    nPorts=1)
    annotation (Placement(transformation(extent={{-10,10},{10,-10}},
        rotation=180,
        origin={176,-40})));
  parameter String weaFil=ModelicaServices.ExternalReferences.loadResource(
      "modelica://Buildings/Resources/weatherdata/USA_CA_San.Francisco.Intl.AP.724940_TMY3.mos")
    "Name of weather data file";
  LibEAS.HeatPumps.WP wP(
    redeclare package Medium_con = Medium_Water,
    redeclare package Medium_eva = Medium_sou,
    mp_nom=mp_nom,
    dp_nom=dp_nom,
    mp_nom_sou=mp_nom_sou,
    dataTable=LibEAS.Data.HeatPumps.Lambda_EU02L(),
    WP(
      use_autoCalc=true,
      Q_useNominal=39000,
      use_refIne=false,
      refIneFre_constant=20,
      use_conCap=false,
      GConIns=10))                                  "Wärmepumpe"
                                                    annotation (Placement(
        transformation(rotation=0, extent={{-66,-24},{-46,-4}})));
  parameter Modelica.Blocks.Interfaces.RealOutput V_nSet_twv_value=1
    "Steuerstrom an das Dreiwegeventil zur Abmischung im Verteiler";
  Modelica.Blocks.Sources.RealExpression boundary_massflow_set(y=0.208)
    "[kg/s], 0.236 kg/s entspricht den 850 kg/h vom Versuchsstand"
    annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={150,-28})));
  LibEAS.Sensors.TemperatureTwoPort_Display WP_senT_RL(redeclare package Medium
      = Medium_Water, m_flow_nominal=mp_nom) annotation (Placement(
        transformation(
        extent={{-10,10},{10,-10}},
        rotation=180,
        origin={-34,-40})));
  Modelica.Blocks.Math.UnitConversions.From_degC from_degC1 annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={62,82})));
  AixLib.Fluid.FixedResistances.Junction V_jun_RL_2(
    redeclare package Medium = Medium_Water,
    m_flow_nominal={mp_nom,mp_nom,mp_nom},
    dp_nominal={dp_nom,dp_nom,dp_nom}) annotation (Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={230,26})));
  AixLib.Fluid.FixedResistances.Junction V_jun_RL_3(
    redeclare package Medium = Medium_Water,
    m_flow_nominal={mp_nom,mp_nom,mp_nom},
    dp_nominal={dp_nom,dp_nom,dp_nom}) annotation (Placement(transformation(
        extent={{-10,10},{10,-10}},
        rotation=270,
        origin={230,-30})));
  LibEAS.Sensors.TemperatureTwoPort_Display B_senT_RL(redeclare package Medium
      = Medium_Water, m_flow_nominal=mp_nom) annotation (Placement(
        transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={230,-60})));
  LibEAS.Sensors.PressureDrop_Display B_dp_Bypass(
    redeclare package Medium = Medium_Water,
    m_flow_nominal=mp_nom,
    dp_nominal=500000*100) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={230,-2})));
  LibEAS.Controls.Heizkurve_gleitend heizkurve_gleitend(
    t_mean=10800,
    T_AU_1=-14,
    T_AU_2=15,
    T_VL_1=75,
    T_VL_2=32)
    annotation (Placement(transformation(extent={{-140,54},{-120,74}})));
  Modelica.Blocks.Sources.BooleanExpression agent_control(y=
        agent_control_setting)                                     annotation (
      Placement(transformation(
        extent={{-15,-9},{15,9}},
        rotation=0,
        origin={1,83})));
  Modelica.Blocks.Logical.Switch switch_control_setting annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={36,82})));
  parameter Modelica.Blocks.Interfaces.BooleanOutput agent_control_setting=
      false "twv control: true -> Agent, false -> PID controller";
  Modelica.Blocks.Interfaces.RealOutput nSet_WP
    annotation (Placement(transformation(extent={{-32,104},{-20,116}}),
        iconTransformation(extent={{-32,104},{-20,116}})));
  Modelica.Blocks.Interfaces.RealOutput T_sou_WP
    annotation (Placement(transformation(extent={{-7,-7},{7,7}},
        rotation=0,
        origin={-81,-21}),  iconTransformation(extent={{-7,-7},{7,7}}, origin={-81,-21})));
  Modelica.Blocks.Interfaces.RealOutput T_RL_WP
    annotation (Placement(transformation(extent={{-7,-7},{7,7}},
        rotation=0,
        origin={-11,-19}),  iconTransformation(extent={{-7,-7},{7,7}}, origin={-11,-19})));
  Modelica.Blocks.Interfaces.RealOutput T_VL_Gebaeude
    annotation (Placement(transformation(extent={{104,26},{116,38}}),
        iconTransformation(extent={{104,26},{116,38}})));
  Modelica.Blocks.Interfaces.RealOutput T_RL_Gebaeude
    annotation (Placement(transformation(extent={{-7,-7},{7,7}},
        rotation=270,
        origin={205,-87}),
        iconTransformation(extent={{204,-94},{218,-80}})));
  Modelica.Blocks.Interfaces.RealOutput T_room
    annotation (Placement(transformation(extent={{274,-32},{288,-18}}),
        iconTransformation(extent={{274,-32},{288,-18}})));
  AixLib.Fluid.Sensors.RelativePressure VS_senRelPre annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=270,
        origin={82,-22})));
  parameter Real CTRL_TWV_k=0.02 "Gain of controller";
  parameter Modelica.Units.SI.Time CTRL_TWV_Ti=120
    "Time constant of Integrator block";
  parameter Modelica.Units.SI.Time CTRL_TWV_Td=0
    "Time constant of Derivative block";
  parameter Real CTRL_WP_k=5 "Gain of controller";
  parameter Modelica.Units.SI.Time CTRL_WP_Ti=500
    "Time constant of Integrator block";
  parameter Modelica.Units.SI.Time CTRL_WP_Td=0
    "Time constant of Derivative block";
  LibEAS.Controls.PI_reset_zero CTRL_WP_PI(
    k=CTRL_WP_k,
    Ti=CTRL_WP_Ti,
    Td=CTRL_WP_Td,
    yMin=WP_nSet_min,
    y_start=1)
    annotation (Placement(transformation(extent={{-50,58},{-30,78}})));
  parameter Real WP_dT_on=2.8
    "if off and control error > eOn, switch to set point tracking";
  parameter Real WP_dT_off=-7.2 "if on and control error < eOff, set y=0";
  parameter Real WP_nSet_min=0.001 "Lower limit of output";
  Modelica.Blocks.Math.UnitConversions.From_degC from_degC2 annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-108,104})));
  Modelica.Blocks.Sources.BooleanExpression WP_manual_control(y=
        WP_manual_control_setting) annotation (Placement(transformation(
        extent={{-20.5,-9.5},{20.5,9.5}},
        rotation=0,
        origin={-122.5,84.5})));
  Modelica.Blocks.Logical.Switch switch_control_setting1
                                                        annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={-82,80})));
  parameter Modelica.Blocks.Interfaces.BooleanOutput WP_manual_control_setting=
      false "Value of Boolean output";
  Modelica.Blocks.Sources.BooleanExpression hil_mode(y=hil_mode_setting)
    annotation (Placement(transformation(
        extent={{-12,-9},{12,9}},
        rotation=0,
        origin={154,85})));
  Modelica.Blocks.Logical.Switch switch_control_setting2
                                                        annotation (Placement(
        transformation(
        extent={{-10,-10},{10,10}},
        rotation=270,
        origin={172,58})));
  Modelica.Blocks.Math.UnitConversions.From_degC from_degC3 annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={174,106})));
  parameter Modelica.Blocks.Interfaces.BooleanOutput hil_mode_setting=false
    "Value of Boolean output";
  Modelica.Blocks.Interfaces.RealInput WP_T_VL annotation (Placement(
        transformation(extent={{-146,94},{-124,116}}),  iconTransformation(
          extent={{-146,94},{-124,116}})));
  Modelica.Blocks.Interfaces.RealInput HIL_T_VL annotation (Placement(
        transformation(extent={{134,96},{156,118}}), iconTransformation(extent=
            {{-150,92},{-128,114}})));
  Modelica.Blocks.Interfaces.RealInput agent_T_VL annotation (Placement(
        transformation(
        extent={{-12,-12},{12,12}},
        rotation=0,
        origin={0,100}),  iconTransformation(extent={{-78,100},{-54,124}})));
  Modelica.Blocks.Interfaces.RealOutput Q_WP annotation (Placement(
        transformation(
        extent={{-7,-7},{7,7}},
        rotation=0,
        origin={37,25}), iconTransformation(extent={{-7,-7},{7,7}}, origin={-7,
            -13})));
  LibEAS.Controls.PI_reset_zero CTRL_DWV(
    k=CTRL_TWV_k,
    Ti=CTRL_TWV_Ti,
    Td=CTRL_TWV_Td,
    yMin=0.01,
    reverseActing=true,
    y_start=1)
    annotation (Placement(transformation(extent={{102,56},{122,76}})));
  Modelica.Blocks.Interfaces.RealOutput T_VL_WP annotation (Placement(
        transformation(
        extent={{-7,-7},{7,7}},
        rotation=0,
        origin={-11,29}), iconTransformation(extent={{-7,-7},{7,7}}, origin={-7,
            -13})));
  Modelica.Blocks.Sources.BooleanExpression booleanExpression1(y=true)
    annotation (Placement(transformation(extent={{82,88},{102,108}})));
  Modelica.Blocks.Sources.RealExpression T_VL_Gebaeude_fix(y=100) annotation (
      Placement(transformation(
        extent={{-10,-10},{10,10}},
        rotation=0,
        origin={0,64})));
  LibEAS.Controls.Hysterese CTRL_WP_OO(eOn=WP_dT_on, eOff=WP_dT_off)
    annotation (Placement(transformation(extent={{-58,90},{-38,110}})));
equation
  connect(B_EG.weaBus, B_weaDat.weaBus) annotation (Line(
      points={{278,4},{280,4},{280,62},{234,62}},
      color={255,204,51},
      thickness=0.5));
  connect(WP_senT_VL_sou.port_b, WP_dp_VL_sou.port_a)
    annotation (Line(points={{-86,12},{-94,12}},       color={0,127,255}));
  connect(WP_dp_VL_sou.port_b, KK_sin.ports[1])
    annotation (Line(points={{-114,12},{-118,12}},     color={0,127,255}));
  connect(re_mp_sou_set.y, WP_pum_RL_sou.m_flow_in) annotation (Line(points={{-109.3,
          -16},{-106,-16},{-106,-28}},    color={0,0,127}));
  connect(WP_senH.H_flow, WP_senQ.u2) annotation (Line(points={{44,-29},{44,-4},
          {44.075,-4},{44.075,2.1}},   color={0,0,127}));
  connect(weaBus.TDryBul, KK_sou.T_in) annotation (Line(
      points={{-152,-36},{-140,-36}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%first",
      index=-1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(B_weaDat.weaBus, weaBus) annotation (Line(
      points={{234,62},{280,62},{280,8},{290,8},{290,-108},{172,-108},{172,-86},
          {-152,-86},{-152,-36}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%second",
      index=1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(B_EG.surf_conBou[1], B_SOIL.opa_b) annotation (Line(points={{271.6,
          -10.85},{270,-10.85},{270,-32},{269.333,-32},{269.333,-35.9333}},
                                                            color={191,0,0}));
  connect(B_T_soil_deep.port, B_SOIL.opa_a) annotation (Line(points={{270,-78},
          {269.333,-78},{269.333,-56}},  color={191,0,0}));
  connect(V_dwv.port_3, V_jun_RL_1.port_3) annotation (Line(points={{18,2},{18,
          -30}},           color={0,127,255}));
  connect(WP_senT_VL.port_b, WP_dp_VL.port_a)
    annotation (Line(points={{-24,12},{-20,12}},   color={0,127,255}));
  connect(WP_pum_RL_sou.port_b, WP_senT_RL_sou.port_a)
    annotation (Line(points={{-96,-40},{-86,-40}},     color={0,127,255}));
  connect(WP_pum_RL_sou.port_a, KK_sou.ports[1])
    annotation (Line(points={{-116,-40},{-118,-40}},   color={0,127,255}));
  connect(wP.sigBus, sigBus) annotation (Line(
      points={{-55.8,-14.2},{-56,-14.2},{-56,32}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%second",
      index=1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(wP.port_a2, WP_senT_VL_sou.port_a) annotation (Line(points={{-65,-5},
          {-65,2},{-66,2},{-66,12}},      color={0,127,255}));
  connect(WP_senT_RL_sou.port_b, wP.port_b2) annotation (Line(points={{-66,-40},
          {-66,-23},{-65,-23}},                                   color={0,127,
          255}));
  connect(VS_senT_VL.port_b, VS_sin_VL.ports[1])
    annotation (Line(points={{104,12},{108,12}},
                                               color={0,127,255}));
  connect(boundary_massflow_set.y, boundary1.m_flow_in) annotation (Line(points={{161,-28},
          {168,-28},{168,-18},{188,-18},{188,-32}},
                    color={0,0,127}));
  connect(boundary_massflow_set.y, boundary.m_flow_in) annotation (Line(points={{161,-28},
          {168,-28},{168,-18},{164,-18},{164,-4}}, color={0,0,127}));
  connect(B_senT_RL.T, boundary1.T_in) annotation (Line(points={{219,-60},{194,
          -60},{194,-36},{188,-36}},                     color={0,0,127}));
  connect(V_jun_RL_2.port_3, B_dp_Bypass.port_a)
    annotation (Line(points={{230,16},{230,8}}, color={0,127,255}));
  connect(B_dp_Bypass.port_b, V_jun_RL_3.port_1)
    annotation (Line(points={{230,-12},{230,-20}}, color={0,127,255}));
  connect(weaBus.TDryBul, heizkurve_gleitend.T_AU) annotation (Line(
      points={{-152,-36},{-152,64},{-139.4,64}},
      color={255,204,51},
      thickness=0.5), Text(
      string="%first",
      index=-1,
      extent={{-6,3},{-6,3}},
      horizontalAlignment=TextAlignment.Right));
  connect(V_jun_RL_3.port_2, B_senT_RL.port_a)
    annotation (Line(points={{230,-40},{230,-50}}, color={0,127,255}));
  connect(B_senT_RL.port_b, B_sin.ports[1])
    annotation (Line(points={{230,-70},{230,-80}}, color={0,127,255}));
  connect(V_jun_RL_3.port_3, B_EG.a_return) annotation (Line(points={{240,-30},
          {248,-30},{248,-6.4},{258,-6.4}}, color={0,127,255}));
  connect(agent_control.y, switch_control_setting.u2) annotation (Line(points={{17.5,83},
          {17.5,82},{24,82}},                              color={255,0,255}));
  connect(WP_senT_RL_sou.T, T_sou_WP) annotation (Line(points={{-76,-29},{-81,
          -29},{-81,-21}},             color={0,0,127}));
  connect(WP_senT_RL.T, T_RL_WP) annotation (Line(points={{-34,-29},{-34,-18},{
          -18,-18},{-18,-19},{-11,-19}},
                       color={0,0,127}));
  connect(VS_senT_VL.T, T_VL_Gebaeude)
    annotation (Line(points={{94,23},{94,32},{110,32}},
                                                     color={0,0,127}));
  connect(B_senT_RL.T, T_RL_Gebaeude)
    annotation (Line(points={{219,-60},{206,-60},{206,-78},{205,-78},{205,-87}},
                                                             color={0,0,127}));
  connect(T_room, B_EG.T_room) annotation (Line(points={{281,-25},{279,-25},{
          279,-12}},                color={0,0,127}));
  connect(V_jun_RL_2.port_2, B_EG.a_supply) annotation (Line(points={{240,26},{
          254,26},{254,-2},{256,-2},{256,-1.9},{257.9,-1.9}},
                                            color={0,127,255}));
  connect(boundary.ports[1], V_jun_RL_2.port_1) annotation (Line(points={{186,4},
          {210,4},{210,26},{220,26}}, color={0,127,255}));
  connect(WP_dp_VL.port_b,V_dwv. port_1) annotation (Line(points={{0,12},{8,12}},
                                         color={0,127,255}));
  connect(V_jun_RL_1.port_1, WP_senH.port_b)
    annotation (Line(points={{28,-40},{34,-40}},   color={0,127,255}));
  connect(WP_senH.port_a, boundary1.ports[1])
    annotation (Line(points={{54,-40},{166,-40}},  color={0,127,255}));
  connect(wP.port_b1, WP_senT_VL.port_a) annotation (Line(points={{-47,-5},{-47,
          12},{-44,12}},                 color={0,127,255}));
  connect(wP.port_a1, WP_senT_RL.port_b) annotation (Line(points={{-47,-23},{
          -46,-23},{-46,-36},{-44,-36},{-44,-40}},
                                            color={0,127,255}));
  connect(WP_senQ.port_b, V_pum_VL.port_a) annotation (Line(points={{54.225,
          11.875},{58,12}},                                  color={0,127,255}));
  connect(V_pum_VL.port_b, VS_senT_VL.port_a) annotation (Line(points={{78,12},
          {84,12}},                               color={0,127,255}));
  connect(nSet_WP, nSet_WP)
    annotation (Line(points={{-26,110},{-26,110}}, color={0,0,127}));
  connect(V_nSet_pum_VL.y, V_pum_VL.dp_in)
    annotation (Line(points={{65,32},{68,32},{68,24}},    color={0,0,127}));
  connect(V_jun_RL_1.port_2, WP_senT_RL.port_a)
    annotation (Line(points={{8,-40},{-24,-40}},     color={0,127,255}));
  connect(VS_senRelPre.port_a, VS_senT_VL.port_a)
    annotation (Line(points={{82,-12},{82,12},{84,12}},
                                                      color={0,127,255}));
  connect(VS_senRelPre.port_b, WP_senH.port_a)
    annotation (Line(points={{82,-32},{82,-40},{54,-40}},color={0,127,255}));
  connect(V_dwv.port_2, WP_senQ.port_a) annotation (Line(points={{28,12},{32,12},
          {32,11.825},{33.825,11.825}},                     color={0,127,255}));
  connect(CTRL_WP_PI.y, sigBus.nSet) annotation (Line(points={{-29,68},{-26,68},
          {-26,50},{-55.95,50},{-55.95,32.05}},
                                        color={0,0,127}), Text(
      string="%second",
      index=1,
      extent={{6,3},{6,3}},
      horizontalAlignment=TextAlignment.Left));
  connect(CTRL_WP_PI.y, nSet_WP)
    annotation (Line(points={{-29,68},{-26,68},{-26,110}},   color={0,0,127}));
  connect(WP_senT_VL.T, CTRL_WP_PI.u_m) annotation (Line(points={{-34,23},{-34,
          38},{-40,38},{-40,56}},        color={0,0,127}));
  connect(from_degC2.y, switch_control_setting1.u1) annotation (Line(points={{-97,104},
          {-94,104},{-94,88}},                       color={0,0,127}));
  connect(heizkurve_gleitend.T_VL, switch_control_setting1.u3) annotation (Line(
        points={{-120,64},{-94,64},{-94,72}},             color={0,0,127}));
  connect(WP_manual_control.y, switch_control_setting1.u2) annotation (Line(
        points={{-99.95,84.5},{-99.95,80},{-94,80}},    color={255,0,255}));
  connect(switch_control_setting1.y, CTRL_WP_PI.u_s) annotation (Line(points={{-71,80},
          {-62,80},{-62,68},{-52,68}},             color={0,0,127}));
  connect(hil_mode.y, switch_control_setting2.u2) annotation (Line(points={{
          167.2,85},{172,85},{172,70}}, color={255,0,255}));
  connect(from_degC3.y, switch_control_setting2.u1) annotation (Line(points={{
          185,106},{188,106},{188,80},{180,80},{180,70}}, color={0,0,127}));
  connect(VS_senT_VL.T, switch_control_setting2.u3) annotation (Line(points={{94,23},
          {94,42},{130,42},{130,70},{164,70}},        color={0,0,127}));
  connect(switch_control_setting2.y, boundary.T_in) annotation (Line(points={{
          172,47},{172,20},{152,20},{152,0},{164,0}}, color={0,0,127}));
  connect(from_degC2.u, WP_T_VL) annotation (Line(points={{-120,104},{-120,105},
          {-135,105}}, color={0,0,127}));
  connect(from_degC3.u, HIL_T_VL)
    annotation (Line(points={{162,106},{162,107},{145,107}}, color={0,0,127}));
  connect(WP_senQ.Q_flow, Q_WP) annotation (Line(points={{55,19},{56,19},{56,24},
          {38,24},{38,25},{37,25}}, color={0,0,127}));
  connect(VS_senT_VL.T, CTRL_DWV.u_m) annotation (Line(points={{94,23},{94,32},
          {100,32},{100,48},{112,48},{112,54}}, color={0,0,127}));
  connect(CTRL_DWV.y, V_dwv.y) annotation (Line(points={{123,66},{123,46},{18,
          46},{18,24}}, color={0,0,127}));
  connect(WP_senT_VL.T, T_VL_WP)
    annotation (Line(points={{-34,23},{-34,29},{-11,29}}, color={0,0,127}));
  connect(booleanExpression1.y, CTRL_DWV.onOff) annotation (Line(points={{103,
          98},{108,98},{108,86},{92,86},{92,72},{100,72}}, color={255,0,255}));
  connect(T_VL_Gebaeude_fix.y, switch_control_setting.u3)
    annotation (Line(points={{11,64},{22,64},{22,74},{24,74}},
                                                       color={0,0,127}));
  connect(from_degC1.u, switch_control_setting.y)
    annotation (Line(points={{50,82},{47,82}}, color={0,0,127}));
  connect(switch_control_setting.u1, agent_T_VL) annotation (Line(points={{24,90},
          {14,90},{14,100},{0,100}},      color={0,0,127}));
  connect(from_degC1.y, CTRL_DWV.u_s) annotation (Line(points={{73,82},{90,82},
          {90,66},{100,66}}, color={0,0,127}));
  connect(switch_control_setting1.y, CTRL_WP_OO.u_s) annotation (Line(points={{
          -71,80},{-66,80},{-66,100},{-60,100}}, color={0,0,127}));
  connect(CTRL_WP_PI.u_m, CTRL_WP_OO.u_m) annotation (Line(points={{-40,56},{
          -40,54},{-60,54},{-60,88},{-48,88}}, color={0,0,127}));
  connect(CTRL_WP_OO.y, CTRL_WP_PI.onOff) annotation (Line(points={{-37,100},{
          -37,84},{-56,84},{-56,80},{-58,80},{-58,74},{-52,74}}, color={255,0,
          255}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false, extent={{-180,
            -130},{320,160}})),
                          Diagram(coordinateSystem(preserveAspectRatio=false,
          extent={{-180,-130},{320,160}}), graphics={
        Rectangle(
          extent={{-62,44},{82,-80}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={170,255,255},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{-144,44},{-56,-80}},
          fillColor={119,230,255},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{82,44},{130,-80}},
          fillColor={119,230,255},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{132,44},{196,-80}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={213,255,170},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{-16,120},{74,52}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={213,170,255},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{198,114},{292,-106}},
          pattern=LinePattern.None,
          fillColor={255,255,170},
          fillPattern=FillPattern.Solid,
          lineColor={0,0,0}),
        Text(
          extent={{148,-70},{206,-78}},
          textColor={28,108,200},
          horizontalAlignment=TextAlignment.Left,
          textString="Schnittstelle"),
        Text(
          extent={{212,112},{284,96}},
          textColor={28,108,200},
          horizontalAlignment=TextAlignment.Left,
          textString="Bauphysik"),
        Rectangle(
          extent={{74,120},{126,52}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={255,170,170},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Text(
          extent={{72,118},{128,112}},
          textColor={28,108,200},
          textString="Regelung DWV"),
        Text(
          extent={{-24,-64},{48,-80}},
          textColor={28,108,200},
          horizontalAlignment=TextAlignment.Left,
          textString="Versuchsstand"),
        Rectangle(
          extent={{132,124},{196,44}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={213,170,255},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{-70,120},{-28,52}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={255,170,170},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Rectangle(
          extent={{-144,120},{-70,52}},
          lineColor={28,108,200},
          lineThickness=1,
          fillColor={213,170,255},
          fillPattern=FillPattern.Solid,
          pattern=LinePattern.None),
        Text(
          extent={{-100,118},{2,112}},
          textColor={28,108,200},
          textString="Regelung WP")}),
    experiment(
      StopTime=108000,
      Interval=29.999988,
      __Dymola_Algorithm="Dassl"),
    Documentation(info="<html>
<p>Model with building, radiators and supplying pumps, connected with a heat source model (Boiler with thermal storage). The parameters of pumps, radiators depends on the room parameters. A control model for the valve position of the radiators exist. </p>
<p>The heat source is also controlled.</p>
<p>Simulating 365d takes 322s</p>
</html>", revisions="<html>
<ul>
<li>TODO: fix problem with room models causing warnings</li>
<li>TODO: Parametrierung der Druckverluste pr&uuml;fen (ist halbwegs plausibel, aber nicht genua kontrolliert)</li>
<li>TODO: Trinkwasserverbraucher erg&auml;nzen?</li>
<li>TODO: check Paramtrierung Fenster</li>
<li>TODO: &uuml;berfl&uuml;ssige parameter des Modells entfernen</li>
<li>2023-02-29 EE erstellt aus <span style=\"font-family: Arial;\">FMI4BIM.Demonstratoren.Townhouse.Version_2021.oneHC_bivalent</span></li>
</ul>
</html>"),
    __Dymola_Commands(file="2024-10-10 1212.mos" "2024-10-10 1212", file=
          "2024-10-10 1754.mos" "2024-10-10 1754"));
end simmodell;
