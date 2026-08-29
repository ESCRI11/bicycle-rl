function paint() {
  const WASH_COLOUR = '#e38c4d'; // Saturated orange-brown wash
  const INK_COLOUR = '#000000';  // Near-black ink

  // Set up wash parameters
  brush.fill(WASH_COLOUR, 80);
  brush.fillBleed(0.1, 'out');
  brush.fillTexture(0.6, 0.4);

  // Draw the main frame of the bicycle
  brush.polygon([
    [-100, 300],
    [100, 300],
    [100, 100],
    [-100, 100]
  ]);

  // Draw the wheels
  brush.circle(-200, 150, 40, true);
  brush.circle(200, 150, 40, true);

  // Draw the spokes
  brush.polygon([
    [-120, 150],
    [-80, 180],
    [-100, 150]
  ]);
  brush.polygon([
    [120, 150],
    [80, 180],
    [100, 150]
  ]);

  brush.polygon([
    [-120, 150],
    [-140, 180],
    [-120, 210]
  ]);
  brush.polygon([
    [120, 150],
    [140, 180],
    [120, 210]
  ]);

  // Set up ink pen for linework
  brush.set('pen', INK_COLOUR, 2);

  // Draw the main frame outline
  brush.line(-100, 300, 100, 300);
  brush.line(-100, 100, 100, 100);

  // Draw the wheels outline
  brush.circle(-200, 150, 40);
  brush.circle(200, 150, 40);

  // Draw the spokes outline
  brush.line(-120, 150, -80, 180);
  brush.line(-100, 150, -80, 180);
  brush.line(120, 150, 80, 180);
  brush.line(100, 150, 80, 180);

  brush.line(-120, 150, -140, 180);
  brush.line(120, 150, 140, 180);
  brush.line(-120, 210, -140, 180);
  brush.line(120, 210, 140, 180);
}
