// reference: what "good" looks like. side view, diamond frame, ink line.
function paint() {
  const R = 100;
  const rear = [-150, 120], front = [150, 120];      // hubs
  const BB = [-20, 112];                             // bottom bracket
  const St = [-78, -60], Sb = [-40, 30];             // seat tube top / mid
  const Ht = [112, -52], Hb = [138, 18];             // head tube top / bottom

  // no vector field on the wheels: it drags the rim off its own hub
  brush.noField();
  brush.wiggle(0.03);

  // washes go down first and the ink goes over them
  brush.fillTexture(0.55, 0.35);
  brush.fillBleed(0.14, 'out');
  brush.fill('#7a6a5f', 52);                         // tyres, soft discs under the rims
  brush.circle(-150, 120, 100, true);
  brush.circle(150, 120, 100, true);
  brush.fill('#c9553a', 60);                         // saddle and bar tape
  brush.circle(-78, -66, 26, true);
  brush.circle(150, -46, 24, true);
  brush.noFill();

  // paint the tubes themselves rather than filling the triangle: a flat polygon reads as
  // a solid panel, a fat marker stroke along each tube reads as paint
  brush.set('marker', '#7fb2c9', 6);
  for (const [a, b] of [[[-78, -60], [-20, 112]], [[-20, 112], [138, 18]],
                        [[-78, -60], [112, -52]], [[-20, 112], [-150, 120]],
                        [[-78, -60], [-150, 120]], [[138, 18], [150, 120]]]) {
    brush.line(a[0], a[1], b[0], b[1]);
  }

  // the polygon's own outline is stroked with the CURRENT brush, so drop back to a fine
  // pale one first or the ground shadow gets a fat coloured border
  brush.set('2H', '#b9b0a4', 1);
  brush.hatchStyle('2H', '#8d8477', 1);              // ground shadow
  brush.hatch(9, 0.15);
  brush.polygon([[-236, 232], [240, 232], [204, 248], [-202, 248]]);
  brush.noHatch();

  // wheels
  brush.set('rotring', '#22221f', 1.4);
  for (const [hx, hy] of [rear, front]) {
    brush.circle(hx, hy, R, false);
    brush.circle(hx, hy, R - 9, false);               // tyre wall
    brush.circle(hx, hy, 7, false);                   // hub
    for (let i = 0; i < 12; i++) {
      const a = (TWO_PI / 12) * i + 0.2;
      brush.line(hx + cos(a) * 7, hy + sin(a) * 7,
                 hx + cos(a) * (R - 12), hy + sin(a) * (R - 12));
    }
  }

  // frame: seat tube, down tube, top tube, chain stay, seat stay, fork, head tube
  brush.set('rotring', '#22221f', 2.6);
  for (const [a, b] of [[St, BB], [BB, Hb], [St, Ht], [BB, rear], [St, rear],
                        [Hb, front], [Ht, Hb]]) {
    brush.line(a[0], a[1], b[0], b[1]);
  }

  // drivetrain: chainring, chain, crank, pedal
  brush.set('rotring', '#22221f', 1.4);
  brush.circle(BB[0], BB[1], 26, false);
  brush.circle(rear[0], rear[1], 12, false);          // sprocket
  brush.line(rear[0], rear[1] - 12, BB[0], BB[1] - 26);
  brush.line(rear[0], rear[1] + 12, BB[0], BB[1] + 26);
  brush.set('rotring', '#22221f', 2.2);
  brush.line(BB[0], BB[1], BB[0] + 10, BB[1] + 40);
  brush.line(BB[0] - 4, BB[1] + 40, BB[0] + 24, BB[1] + 40);

  // saddle
  brush.set('2B', '#22221f', 3);
  brush.spline([[-112, -66], [-90, -74], [-62, -70], [-46, -60]], 0.7);
  brush.line(St[0], St[1], St[0] + 2, St[1] + 8);

  // drop handlebar
  brush.spline([[Ht[0] - 4, Ht[1]], [Ht[0] + 34, Ht[1] - 8], [Ht[0] + 54, Ht[1] + 4],
                [Ht[0] + 46, Ht[1] + 30], [Ht[0] + 22, Ht[1] + 34]], 0.6);
}
