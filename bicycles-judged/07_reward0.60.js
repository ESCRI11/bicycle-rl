function paint() {
  const WASH_COLOUR = '#FF6F61'; // Red wash
  const INK_COLOUR = '#000000';  // Black ink

  // Bicycle frame
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-300, -100],
    [300, -100],
    [300, 100],
    [-300, 100]
  ]);
  brush.noFill();

  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-300, -100, 300, -100);
  brush.line(-300, 100, 300, 100);

  // Wheels
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(-100, -180, 80, false);
  brush.circle(100, -180, 80, false);

  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(-100, -180, 80);
  brush.circle(100, -180, 80);

  // Handlebars
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-10, -150],
    [10, -150],
    [10, -200],
    [-10, -200]
  ]);
  brush.noFill();

  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-10, -150, 10, -150);

  // Seat post
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(0, -100, 0, 0);

  // Chainring
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(0, -200, 20, false);
  brush.noFill();

  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(0, -200, 20);
}
