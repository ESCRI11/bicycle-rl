function paint() {
  let WASH_COLOUR = '#b0b0b0';
  let INK_COLOUR = '#000000';

  // Draw the main body of the bike
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-50, 0],
    [50, 0],
    [50, -200],
    [-50, -200]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-50, 0, 50, 0);
  brush.line(50, 0, 50, -200);
  brush.line(-50, 0, -50, -200);

  // Draw the wheels
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.1, 'out');
  brush.fillTexture(0.5, 0.3);
  brush.circle(-75, -100, 50, false);
  brush.circle(75, -100, 50, false);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(-75, -100, 50, true);
  brush.circle(75, -100, 50, true);

  // Draw the spokes
  brush.set('rotring', INK_COLOUR, 1);
  for (let i = -75; i <= 75; i += 20) {
    brush.line(i, -100, i, -190);
  }
  for (let j = -190; j < -100; j += 10) {
    brush.line(-75, j, 75, j);
  }

  // Draw the handlebars
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [0, 0],
    [-15, 15],
    [15, 15]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(0, 0, -15, 15);
  brush.line(0, 0, 15, 15);

  // Draw the saddlebag
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-50, -220],
    [50, -220],
    [50, -250],
    [-50, -250]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-50, -220, 50, -220);
  brush.line(50, -220, 50, -250);
  brush.line(-50, -220, -50, -250);
}
