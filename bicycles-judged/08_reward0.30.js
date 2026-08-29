function paint() {
  const WASH_COLOUR = '#7851af'; // Purple wash
  const INK_COLOUR = '#0d0d0d'; // Black ink

  // Wash and ink for the main body of the bike
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-250, -100],
    [250, -100],
    [250, -150],
    [-250, -150]
  ]);
  brush.noFill();

  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-250, -100, 250, -100);

  // Wash and ink for the wheels
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(-100, -200, 60);
  brush.circle(100, -200, 60);
  brush.noFill();

  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(-100, -200, 60);
  brush.circle(100, -200, 60);

  // Wash and ink for the handlebars
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-100, -150],
    [100, -150],
    [0, -250]
  ]);
  brush.noFill();

  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-100, -150, 100, -150);
}
