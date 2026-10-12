# Local build: run makepkg -si from this directory.
pkgname=limbus-zh
pkgver=0.1.0
pkgrel=1
pkgdesc='LLC Chinese language pack installer for Steam Proton'
arch=('any')
license=('MIT')
depends=('python' '7zip')
source=('limbus-zh' 'LICENSE' 'README.md')
sha256sums=('15384888a333c479dae4f242413f13f4663bd4f7d2b27bdfc97dba6be3a23cd5'
            '345b7077ae5671ae518e909cf4aa7a7ac44a9361c055ffe665407550ea1d7e4b'
            '80f51a1faf245a3e2be493f752e0803a288469a2e3c962f7559deec9b013c751')
package() {
    install -Dm755 "$srcdir/limbus-zh" "$pkgdir/usr/bin/limbus-zh"
    install -Dm644 "$srcdir/LICENSE" "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
}
