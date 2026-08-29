function paint() {
    const WASH_COLOUR = '#780e8a'; // Purple
    const INK_COLOUR = '#000000'; // Black

    // Draw a purple wash for the body of the bike
    brush.fill(WASH_COLOUR, 120);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([
        [-200, -200],
        [200, -200],
        [200, 100],
        [-200, 100]
    ]);
    brush.noFill();

    // Draw black ink lines for the wheels and frame
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-220, 100, -220, 200);
    brush.line(220, 100, 220, 200);
    brush.circle(-220, 150, 60);
    brush.circle(220, 150, 60);

    // Draw the seat post and handlebars
    brush.line(-50, 150, 50, 150);
    brush.line(0, 150, 0, 180);
    brush.line(0, 180, 30, 210);
    brush.line(0, 180, -30, 210);

    // Draw some loose watercolour washes on the wheels
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.circle(-220, 150, 70, true);
    brush.circle(220, 150, 70, true);
    brush.noFill();

    // Draw ink lines on top of the washes
    brush.set('rotring', INK_COLOUR, 2);
    brush.spline([[-220, 150], [-210, 140], [-200, 150]], 0.3);
    brush.spline([[220, 150], [210, 140], [200, 150]], 0.3);
}
