"""
generate_bio.py
Run before every deploy to regenerate biography.html from index.html.
Keeps both pages in sync automatically.
"""

with open('index.html') as f:
    html = f.read()

# Update meta
html = html.replace(
    '<title>Mary Kilpatrick — Broadway Actress, Figurative Painter | Original Art & Prints</title>',
    '<title>Biography — Mary Kilpatrick</title>'
)
html = html.replace(
    '<meta name="description" content="Mary Kilpatrick — Broadway actress (Bye Bye Birdie, Oh! Calcutta!) turned mixed media painter. Original figurative paintings of women. First edition giclée prints. Ships nationwide.">',
    '<meta name="description" content="Full biography of Mary Kilpatrick — Broadway actress, published illustrator, founder of BEAT Children\'s Theatre, and figurative painter.">'
)
html = html.replace(
    '<link rel="canonical" href="https://www.marykilpatrick.com/">',
    '<link rel="canonical" href="https://www.marykilpatrick.com/biography.html">'
)

# Pre-expand bio
html = html.replace(
    '<div class="bio-full" id="bio-full">',
    '<div class="bio-full open" id="bio-full">'
)

# Remove bio-short
html = html.replace(
    '    <p class="bio-short">From Broadway stages to canvas — vivid, emotionally charged works that celebrate women\'s strength, tenderness, and resilience. Each painting carries the weight of a life spent in service to storytelling.</p>\n',
    ''
)

# Remove Read Full Biography button
html = html.replace(
    '    <button class="learn-more-btn" id="learn-more-btn" onclick="toggleBio()"><span id="learn-more-label">Read Full Biography</span> <span class="arrow">›</span></button>\n',
    ''
)

# Keep only: everything up to the SEO div + footer + simple nav JS
hero_end = html.find('<!-- SEO: Individual painting pages')
footer_start = html.rfind('<footer>')
footer_end = html.rfind('</footer>') + len('</footer>')
footer_html = html[footer_start:footer_end]

biography = html[:hero_end].rstrip()
biography += '\n\n' + footer_html + '''
<script>
function toggleMobileNav() {
  const menu = document.getElementById('nav-mobile');
  const btn = document.getElementById('nav-hamburger');
  menu.classList.toggle('open');
  btn.classList.toggle('open');
}
document.addEventListener('click', e => {
  if (!e.target.closest('nav') && !e.target.closest('.nav-mobile')) {
    document.getElementById('nav-mobile').classList.remove('open');
    document.getElementById('nav-hamburger').classList.remove('open');
  }
});
document.querySelectorAll('.nav-dropdown-toggle').forEach(toggle => {
  toggle.addEventListener('click', e => {
    e.preventDefault();
    const menu = toggle.nextElementSibling;
    menu.style.display = menu.style.display === 'block' ? '' : 'block';
  });
});
document.addEventListener('click', e => {
  if (!e.target.closest('.nav-dropdown')) {
    document.querySelectorAll('.nav-dropdown-menu').forEach(m => m.style.display = '');
  }
});
</script>
</body>
</html>'''

with open('biography.html', 'w') as f:
    f.write(biography)

print("biography.html regenerated from index.html")
