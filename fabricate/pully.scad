// include<filename.scad>;
$fn=150;
mm = 1.;
inch = 25.4 * mm;



AXEL_D = 3 * mm;
AXEL_R = AXEL_D/2;
PULLY_D = 2 * inch;
PULLY_R = PULLY_D / 2.;

BELT_D = .25 * inch;
BELT_R = BELT_D / 2.;

PULLY_H = .5 * inch;

module pully(){
  intersection(){
    difference(){
      union(){
	cylinder(h=PULLY_H, r=PULLY_R); 
     }
      union(){
	translate([0, 0, PULLY_H/2])rotate_extrude(convexity=10)translate([PULLY_R - BELT_R, 0, 0])circle(r=BELT_R);
	difference(){
	  translate([0, 0, PULLY_H/4])cylinder(h=BELT_D, r=PULLY_R + BELT_R);
	  translate([0, 0, PULLY_H/4 - 1])cylinder(h=BELT_D + 2, r=PULLY_R - BELT_R);
	}
	translate([0, 0, -1])cylinder(h=PULLY_H + 2, r=AXEL_R);
      }
    }
  }
}

pully();
