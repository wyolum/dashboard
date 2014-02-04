$fn=150;
mm = 1.;
inch = 25.4 * mm;

AXLE_R = 8 * mm / 2;
GAP =.5 * mm;

WIDTH = 1 * inch;
SCREW_R = .125 * inch;
SCREW_SEP = 20 * mm;


BASE_H = 10 * mm;
BASE_L = 2 * inch;
BASE_W = WIDTH;
AXLE_STOP_THICKNESS = 5 * mm;

TRACK_W = .25 * inch;
TRACK_H = .1 * inch;

TOP_L = BASE_L - 2 * BASE_H;
TOP_H = 7 * mm;
module base(){
  intersection(){
    translate([-BASE_L/2, -WIDTH/2, 0])rotate(v=[0, 1, 0], a=45)cube([BASE_L / sqrt(2), WIDTH, BASE_L / sqrt(2)]);
    difference(){
      union(){
	translate([-BASE_L/2, -BASE_W/2, 0])cube([BASE_L, BASE_W, BASE_H]);
	translate([-BASE_L/2, -TRACK_W/2, -TRACK_H])cube([BASE_L, TRACK_W, TRACK_H + 1]);
      }
      union(){
	translate([0, -BASE_W/2 + AXLE_STOP_THICKNESS, BASE_H])rotate(v=[-1, 0, 0], a=90)cylinder(r = AXLE_R, h=BASE_W); // axle hole
	translate([-SCREW_SEP/2, 0, -1 - TRACK_H])cylinder(r=SCREW_R, h=BASE_H + TRACK_H + 2);
	translate([SCREW_SEP/2, 0, -1 - TRACK_H])cylinder(r=SCREW_R, h=BASE_H + TRACK_H + 2);
      }
    }
  }
}

module top(){
    difference(){
      union(){
	translate([-TOP_L/2, -BASE_W/2, TOP_H + GAP])cube([TOP_L, BASE_W, TOP_H]);
      }
      union(){
	translate([0, -BASE_W/2 + AXLE_STOP_THICKNESS, TOP_H])rotate(v=[-1, 0, 0], a=90)cylinder(r = AXLE_R, h=BASE_W);
	translate([-SCREW_SEP/2, 0, GAP])cylinder(r=SCREW_R, h=BASE_H + TRACK_H + 2);
	translate([SCREW_SEP/2, 0, GAP])cylinder(r=SCREW_R, h=BASE_H + TRACK_H + 2);
      }
    }
}
// translate([0, 0, 10])top();
// base();
