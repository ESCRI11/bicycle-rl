function paint() {
    const WASH_COLOUR = '#e6b800'; // Gold
    const INK_COLOUR = '#000000'; // Black

    // Wash for the main body of the bicycle
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([
        [-150, 0],
        [150, 0],
        [150, 100],
        [-150, 100]
    ]);
    brush.noFill();

    // Ink line for the frame
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-150, 0, 150, 0);
    brush.line(-150, 50, 150, 50);
    brush.line(-150, 0, -150, 100);
    brush.line(150, 0, 150, 100);

    // Wheels
    brush.set('rotring', INK_COLOUR, 2);
    brush.circle(-100, 0, 60);
    brush.circle(100, 0, 60);

    // Wash for the spokes
    brush.fill('#ffffff', 120);
    brush.fillTexture(0.1, 0.1);
    brush.spline([
        [-120, 50],
        [-120, 10],
        [-100, -30]
    ], 0.2);
    brush.spline([
        [120, 50],
        [120, 10],
        [100, -30]
    ], 0.2);

    // Wash for the seat
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([
        [-50, 100],
        [50, 100],
        [50, 130],
        [-50, 130]
    ]);
    brush.noFill();

    // Wash for pedals
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([
        [-30, 80],
        [-20, 80],
        [-20, 110],
        [-30, 110]
    ]);
    brush.polygon([
        [30, 80],
        [20, 80],
        [20, 110],
        [30, 110]
    ]);
    brush.noFill();
}
