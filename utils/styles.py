# Material Design benzeri renkler
COLORS = {
    'primary': '#2196F3',  # Mavi
    'secondary': '#FF4081',  # Pembe
    'success': '#4CAF50',  # Yeşil
    'warning': '#FFC107',  # Sarı
    'error': '#F44336',  # Kırmızı
    'background': '#FAFAFA',  # Açık gri
    'surface': '#FFFFFF',  # Beyaz
    'text': '#212121',  # Koyu gri
}

def adjust_color(hex_color, factor):
    # Renk tonunu açık/koyu yapmak için yardımcı fonksiyon
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = min(255, int(r * factor))
    g = min(255, int(g * factor))
    b = min(255, int(b * factor))
    return f'#{r:02x}{g:02x}{b:02x}'