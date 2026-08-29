function paint() {
  const WASH_COLOUR = '#3e8c3d';
  const INK_COLOUR = '#000000';

  // Draw the frame of the bicycle
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(-50, 0, 40, true);
  brush.circle(50, 0, 40, true);
  brush.circle(-50, 0, 40, false);
  brush.circle(50, 0, 40, false);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-50, 40, 50, 40);
  brush.line(-50, -40, 50, -40);

  // Draw the handlebars
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(80, -10, 30, false);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(80, 30, 80, 60);

  // Draw the wheels
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.circle(-120, 150, 100, true);
  brush.circle(120, 150, 100, true);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(-120, 150, 100, false);
  brush.circle(120, 150, 100, false);
  brush.circle(-120, 150, 20, true);
  brush.circle(120, 150, 20, true);
  brush.circle(-120, 150, 20, false);
  brush.circle(120, 150, 20, false);

  // Draw the seat
  brush.fill(WASH_COLOUR, 90);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-50, 40],
    [-100, 100],
    [100, 100],
    [50, 40]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-50, 40, -100, 100);
  brush.line(-100, 100, 100, 100);
  brush.line(100, 100, 50, 40);
}
