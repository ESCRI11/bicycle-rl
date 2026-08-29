function paint() {
  const WASH_COLOUR = '#ffcccb';
  const INK_COLOUR = '#000000';

  // Wash for the frame and wheels
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.spline([[ -200, 200 ], [ -100, 100 ], [ 100, 100 ], [ 200, 200 ]]);
  brush.spline([[ -180, -200 ], [ -120, -140 ], [ 120, -140 ], [ 180, -200 ]]);
  brush.noFill();

  // Ink line for the frame
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-200, 200, 200, 200);
  brush.line(-200, -200, 200, -200);
  brush.line(-200, 200, -200, -200);
  brush.line(200, 200, 200, -200);

  // Wash for the wheels
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(-100, 100, 50, true);
  brush.circle(100, 100, 50, true);
  brush.noFill();

  // Ink line for the wheels
  brush.set('rotring', INK_COLOUR, 1);
  brush.circle(-100, 100, 50);
  brush.circle(100, 100, 50);

  // Wash for the seat
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.spline([[ -50, 0 ], [ 50, 0 ], [ 0, 150 ]]);
  brush.noFill();

  // Ink line for the seat
  brush.set('rotring', INK_COLOUR, 2);
  brush.spline([[ -50, 0 ], [ 50, 0 ], [ 0, 150 ]]);

  // Wash for the pedals
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.spline([[ -50, -50 ], [ 0, -30 ], [ 50, -50 ]]);
  brush.spline([[ -50, 50 ], [ 0, 30 ], [ 50, 50 ]]);
  brush.noFill();

  // Ink line for the pedals
  brush.set('rotring', INK_COLOUR, 2);
  brush.spline([[ -50, -50 ], [ 0, -30 ], [ 50, -50 ]]);
  brush.spline([[ -50, 50 ], [ 0, 30 ], [ 50, 50 ]]);

  // Wash for the handlebars
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.spline([[ 200, 200 ], [ 300, 200 ], [ 300, -50 ], [ 200, -50 ]]);
  brush.noFill();

  // Ink line for the handlebars
  brush.set('rotring', INK_COLOUR, 2);
  brush.spline([[ 200, 200 ], [ 300, 200 ], [ 300, -50 ], [ 200, -50 ]]);
}
