function paint() {
  const WASH_COLOUR = '#8b4513';
  const INK_COLOUR = '#000000';

  // Wash
  brush.fill(WASH_COLOUR, 100);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-200, -250],
    [200, -250],
    [200, 150],
    [-200, 150]
  ]);
  brush.noFill();

  // Ink
  brush.set('rotring', INK_COLOUR, 2);
  brush.line(-200, -250, 200, -250);
  brush.line(-200, 150, 200, 150);

  brush.set('rotring', INK_COLOUR, 1);
  brush.spline(
    [[-100, -220], [-50, -150], [50, -150], [100, -220]],
    0.2
  );

  brush.circle(-80, -100, 40, true);
  brush.circle(80, -100, 40, true);
}
