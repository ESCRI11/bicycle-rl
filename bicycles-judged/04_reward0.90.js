function paint() {
  const WASH_COLOUR = '#ffcccb';
  const INK_COLOUR = '#000000';

  // Wash and ink the front wheel
  brush.fill(WASH_COLOUR, 100);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.8, 0.6);
  brush.circle(-250, -100, 150, true);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(-250, -100, 150);

  // Wash and ink the back wheel
  brush.fill(WASH_COLOUR, 100);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.8, 0.6);
  brush.circle(250, -100, 150, true);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.circle(250, -100, 150);

  // Wash and ink the frame
  brush.fill(WASH_COLOUR, 100);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.7, 0.5);
  brush.spline([
    [-300, -100],
    [-200, -100],
    [-200, -200],
    [200, -200],
    [200, -100],
    [300, -100]
  ], 0.5);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 4);
  brush.spline([
    [-300, -100],
    [-200, -100],
    [-200, -200],
    [200, -200],
    [200, -100],
    [300, -100]
  ]);

  // Wash and ink the handlebars
  brush.fill(WASH_COLOUR, 100);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.6, 0.4);
  brush.polygon([
    [-150, -150],
    [-100, -150],
    [-100, -200],
    [-150, -200]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.polygon([
    [-150, -150],
    [-100, -150],
    [-100, -200],
    [-150, -200]
  ]);

  // Wash and ink the saddle
  brush.fill(WASH_COLOUR, 100);
  brush.fillBleed(0.15, 'out');
  brush.fillTexture(0.7, 0.5);
  brush.polygon([
    [0, -150],
    [0, -250],
    [100, -200],
    [100, -150]
  ]);
  brush.noFill();
  brush.set('rotring', INK_COLOUR, 2);
  brush.polygon([
    [0, -150],
    [0, -250],
    [100, -200],
    [100, -150]
  ]);
}
