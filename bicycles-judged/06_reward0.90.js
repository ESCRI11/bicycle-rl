function paint() {
    const WASH_COLOUR = '#ff0000';
    const INK_COLOUR = '#000000';

    // Wash for the wheels
    brush.fill(WASH_COLOUR, 120);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.circle(-200, 0, 100, false);
    brush.circle(200, 0, 100, false);
    brush.noFill();

    // Ink the wheels
    brush.set('rotring', INK_COLOUR, 2);
    brush.circle(-200, 0, 80, false);
    brush.circle(200, 0, 80, false);

    // Wash for the body
    brush.fill(WASH_COLOUR, 100);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.spline([[-150, -100], [-100, -100], [-50, -200], [50, -200], [100, -100], [150, -100]], 0.5);
    brush.noFill();

    // Ink the body
    brush.set('rotring', INK_COLOUR, 4);
    brush.spline([[-150, -100], [-100, -100], [-50, -200], [50, -200], [100, -100], [150, -100]], 0.5);

    // Wash for the handlebars
    brush.fill(WASH_COLOUR, 80);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([[100, -150], [150, -120], [130, -120], [130, -130], [100, -150]]);
    brush.noFill();

    // Ink the handlebars
    brush.set('rotring', INK_COLOUR, 2);
    brush.polygon([[100, -150], [150, -120], [130, -120], [130, -130], [100, -150]]);

    // Wash for the seat stays
    brush.fill(WASH_COLOUR, 120);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.polygon([[0, -250], [-25, -200], [0, -170], [25, -200]]);
    brush.noFill();

    // Ink the seat stays
    brush.set('rotring', INK_COLOUR, 2);
    brush.polygon([[0, -250], [-25, -200], [0, -170], [25, -200]]);
}
