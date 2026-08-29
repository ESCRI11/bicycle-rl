function paint() {
  const WASH_COLOUR = '#4c4b4b'; // Rich dark gray wash
  const INK_COLOUR = '#101010'; // Near-black ink

  // Bicycle frame
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-100, -50],
    [100, -50],
    [100, 50],
    [-100, 50]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-100, -50, 100, -50);
  brush.line(-100, 50, 100, 50);
  brush.line(-100, -50, -100, 50);
  brush.line(100, -50, 100, 50);

  // Bike wheels
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(150, 0, 100, true);
  brush.circle(-150, 0, 100, true);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(150, 0, 80);
  brush.circle(-150, 0, 80);
  brush.circle(150, 0, 10);
  brush.circle(-150, 0, 10);

  // Bike handlebars
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-50, 0],
    [-100, 50],
    [-50, 100],
    [0, 75]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-50, 0, -100, 50);
  brush.line(-50, 0, -50, 100);
  brush.line(-50, 0, 0, 75);
}
