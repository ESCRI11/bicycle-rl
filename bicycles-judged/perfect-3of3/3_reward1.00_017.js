function paint() {
    const WASH_COLOUR = '#a1c4d4'; // Light blue for the wash
    const INK_COLOUR = '#000000';  // Black for the ink

    // Bike frame (main body)
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([
        [-300, 50],
        [-150, 50],
        [-150, -200],
        [-300, -200]
    ]);
    brush.noFill();
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-300, -200, -150, -200);

    // Seat stays
    brush.fill(WASH_COLOUR, 80);
    brush.polygon([
        [-160, -50],
        [-140, -100],
        [-100, -100],
        [-120, -50]
    ]);
    brush.noFill();
    brush.set('rotring', INK_COLOUR, 1.5);
    brush.line(-160, -50, -140, -100);
    brush.line(-120, -50, -100, -100);

    // Fork
    brush.fill(WASH_COLOUR, 80);
    brush.polygon([
        [300, -50],
        [250, -100],
        [150, -100],
        [200, -50]
    ]);
    brush.noFill();
    brush.set('rotring', INK_COLOUR, 1.5);
    brush.line(300, -50, 250, -100);
    brush.line(200, -50, 150, -100);

    // Wheels
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.circle(-180, -180, 100);
    brush.circle(220, -180, 100);
    brush.noFill();
    brush.set('rotring', INK_COLOUR, 2);
    brush.circle(-180, -180, 100);
    brush.circle(220, -180, 100);

    // Spokes
    brush.set('rotring', INK_COLOUR, 1);
    for (let i = 0; i < 20; i++) {
        let theta = map(i, 0, 19, 0, TWO_PI);
        let len = map(cos(theta), -1, 1, 150, 100);
        brush.line(-180, -180, -180 + len * cos(theta), -180 - len * sin(theta));
    }
    for (let i = 0; i < 20; i++) {
        let theta = map(i, 0, 19, 0, TWO_PI);
        let len = map(cos(theta), -1, 1, 150, 100);
        brush.line(220, -180, 220 + len * cos(theta), -180 - len * sin(theta));
    }

    // Seat
    brush.fill(WASH_COLOUR, 80);
    brush.polygon([
        [-100, -200],
        [-50, -250],
        [50, -250],
        [100, -200]
    ]);
    brush.noFill();
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-100, -200, -50, -250);
    brush.line(100, -200, 50, -250);
}
