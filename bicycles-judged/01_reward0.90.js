function paint() {
    const WASH_COLOUR = '#87CEEB'; // Sky blue wash
    const INK_COLOUR = '#000000'; // Black ink

    // Draw bicycle frame
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-100, -100, 100, -100);
    brush.line(-50, -100, -50, 50);
    brush.line(50, -100, 50, 50);
    brush.line(50, 50, -50, 50);

    // Draw wheels
    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.circle(-70, 30, 40);
    brush.noFill();

    brush.set('rotring', INK_COLOUR, 2);
    brush.circle(-70, 30, 40);

    brush.fill(WASH_COLOUR, 90);
    brush.fillBleed(0.15, 'out');
    brush.fillTexture(0.6, 0.4);
    brush.circle(70, 30, 40);
    brush.noFill();

    brush.set('rotring', INK_COLOUR, 2);
    brush.circle(70, 30, 40);

    // Draw seat post
    brush.line(0, -100, 0, 20);

    // Draw handlebars
    brush.line(-100, -130, -70, -130);
    brush.line(-50, -150, -20, -150);
    brush.line(-20, -150, -20, -130);
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(-20, -150, 0, -150);

    // Draw chainstay
    brush.set('rotring', INK_COLOUR, 2);
    brush.line(0, -100, 20, -100);
}
