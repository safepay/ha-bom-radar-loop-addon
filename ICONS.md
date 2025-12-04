# Addon Icons

For a complete addon appearance in Home Assistant, you can add the following optional image files to the repository root:

## icon.png
- **Size**: 256x256 pixels (or smaller, will be scaled)
- **Format**: PNG with transparency
- **Purpose**: Shown in the addon store list
- **Suggestion**: A radar icon, weather icon, or Australian map with radar waves

## logo.png
- **Size**: Varies (typically 256x256 to 512x512)
- **Format**: PNG with transparency
- **Purpose**: Shown on the addon details page
- **Suggestion**: Same as icon.png or a more detailed version

## Creating Icons

You can create simple icons using:
1. Free icon sites like [Flaticon](https://www.flaticon.com/) (search for "radar" or "weather")
2. Image editors like GIMP, Photoshop, or online tools like [Canva](https://www.canva.com/)
3. AI image generators

## Adding Icons

Once you have your images:
1. Save them as `icon.png` and `logo.png` in the repository root
2. Commit and push to the repository
3. Home Assistant will automatically use them

## Note

Icons are optional. The addon will work perfectly without them, but they make the addon look more professional in the Home Assistant addon store.
