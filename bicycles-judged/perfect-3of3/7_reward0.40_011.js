function paint() {
  const WASH_COLOUR = '#FF4500'; // Orange for the wheels and handlebars
  const INK_COLOUR = '#000000'; // Black for the linework

  // Draw the bicycle frame
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.polygon([
    [-150, -200],
    [-150, -150],
    [150, -150],
    [150, -200],
    [-50, -300],
    [50, -300]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-150, -200, -150, -150);
  brush.line(150, -200, 150, -150);
  brush.line(-50, -300, 50, -300);
  brush.line(-100, -300, 100, -300);

  // Draw the rear wheel
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(-100, -160, 60, true);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(-100, -160, 60);

  // Draw the front wheel
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(100, -160, 60, true);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(100, -160, 60);

  // Draw the saddle
  brush.fill(WASH_COLOUR, 70);
  brush.fillBleed(0.15, 'out');
  brush.circle(0, -250, 30);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(0, -250, 30);

  // Draw the handlebars
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.15, 'out');
  brush.polygon([
    [-100, -150],
    [-150, -130],
    [-100, -110],
    [-50, -130]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-100, -150, -100, -110);
  brush.line(-50, -130, -50, -150);
}
