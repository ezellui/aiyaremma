let hue, modulusColor, defaultHue;
switch (colorScheme) {
    case 'standard':
        hue = normalizedPhase * 360;
        [r, g, b] = hsvToRgb(hue, 0.8, brightness);
        break;
    
    // ...
    
    case 'modulus':
        modulusColor = 0.5 + 0.5 * Math.tanh(modulus / 2);
        r = g = b = Math.floor(modulusColor * 255);
        break;
        
    default:
        defaultHue = normalizedPhase * 360;
        [r, g, b] = hsvToRgb(defaultHue, 0.8, brightness);
}