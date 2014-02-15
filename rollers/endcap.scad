include<axle_foot.scad>;
$fn=150;
mm = 1.;
inch = 25.4 * mm;

ROLLER_L = 24 * inch;
ROLLER_R = 1.5 * inch;
ROLLER_T = .125 * inch;
AXLE_D = 8 * mm;
BELT_R = 5/2. * mm;
TOTAL_H = 40 * mm;
RACE_H = 10 * mm;
BEARING_R = 11.2 * mm;
BEARING_H = 7 * mm;
WALL_T = 3 * mm;
SLEEVE_OR = 10*mm / 2;
SLEEVE_IR = 8*mm / 2;
SLEEVE_H = 12*mm;
ID_TOLERANCE = .1*mm;

module bearing(){
  difference(){
    cylinder(h=BEARING_H, r=BEARING_R);
    translate([0, 0, -1])cylinder(h=BEARING_H + 2, r=AXLE_D / 2);
  }
}

module sleeve(){
  difference(){
    cylinder(h=SLEEVE_H, r=SLEEVE_OR);
    translate([0, 0, -.01])cylinder(h=SLEEVE_H + .02, r=SLEEVE_IR);
  }
}

module endcap(){
  translate([0, 0, 0 * inch])
  difference(){
    union(){
      cylinder(h=TOTAL_H, r=ROLLER_R - ROLLER_T-ID_TOLERANCE);
      cylinder(h=RACE_H, r=ROLLER_R);
    }
    union(){
      translate([0, 0, -1])cylinder(h=RACE_H + 2 * BEARING_H, r=BEARING_R);
      translate([0, 0, -1])cylinder(h=TOTAL_H + 1, r=AXLE_D/2. + 0.5*mm);
      translate([0, 0, RACE_H/2])rotate_extrude(convexity = 10)translate([ROLLER_R + 1*mm, 0, 0])circle(r = BELT_R * mm, $fn = 100);
      translate([0, 0, RACE_H + 2 * BEARING_H + WALL_T])cylinder(r1=AXLE_D / 2, r2 = ROLLER_R - WALL_T, h=TOTAL_H - (RACE_H + 2 * BEARING_H) - WALL_T + 1);
    }
  }
}

module roller(){
  difference(){
    translate([0, 0,  0])cylinder(h=ROLLER_L, r=ROLLER_R);
    translate([0, 0, -1])cylinder(h=ROLLER_L + 2, r=ROLLER_R - ROLLER_T);
  }
}
module axle(){
  color([0, 0, 0])cylinder(h=ROLLER_L + SLEEVE_H * 2, r=AXLE_D/2);
}

difference(){
  union(){
    // translate([0, 0, RACE_H])color([0, 1, 0])roller();
    color([1, 0, 0])endcap();
    //color([1, 1, 1])translate([0, 0, RACE_H])bearing();
    //color([1, 1, 1])translate([0, 0, RACE_H + BEARING_H])bearing();
    //color([1, 1, 1])translate([0, 0, RACE_H + BEARING_H])bearing();
    //color([1, 0, 1])translate([0, 0, 0])translate([0, 0, RACE_H - SLEEVE_H])sleeve();
  }
  //translate([-1 - ROLLER_R, -1, -1])cube([2 * ROLLER_R + 2, ROLLER_R + 1, TOTAL_H + 2]);
}
//color([1, 1, 1])translate([0, 0, RACE_H])bearing();
//color([1, 1, 1])translate([0, 0, RACE_H + BEARING_H])bearing();
//color([1, 0, 1])translate([0, 0, 0])translate([0, 0, RACE_H - SLEEVE_H])sleeve();
//translate([0, 0, -1*inch]) axle();
