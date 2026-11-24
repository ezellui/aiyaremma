case 'standard':
    const hue = normalizedPhase * 360;  // Объявление константы в case
    [r, g, b] = hsvToRgb(hue, 0.8, brightness);
    break;
    
// ...

case 'modulus':
    const modulusColor = 0.5 + 0.5 * Math.tanh(modulus / 2);  // Ещё одно объявление
    r = g = b = Math.floor(modulusColor * 255);
    break;
    
default:
    const defaultHue = normalizedPhase * 360;  // И ещё одно
    [r, g, b] = hsvToRgb(defaultHue, 0.8, brightness);