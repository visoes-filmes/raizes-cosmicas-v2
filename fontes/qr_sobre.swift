// O QR POR CIMA DO ESPELHO (26/09). "O QR code nao esta aparecendo."
//
// Com o oculos na cabeca o projetor mostra o espelho do Quest (scrcpy, em tela
// cheia, num Space proprio do macOS) -- e o QR so existia na pagina da animacao,
// que fica por baixo. Este programinha poe o QR numa janela sem borda, que nao
// recebe clique nem foco, acima de tudo e em todos os Spaces do projetor, no
// mesmo lugar e tamanho do QR da animacao (projecao.html): a troca espelho <->
// animacao nao mexe o QR. Em retroprojecao (--espelhar 1) vai para o outro canto
// e sai invertido, para quem olha do outro lado do tule le-lo certo.
//
// A Cabine compila isto uma vez (swiftc, fica em $TMPDIR/raizes-qr) e abre/fecha
// junto com o espelho do projetor:
//
//   raizes-qr --tela "ViewSonic PJ" --espelhar 1 --img fontes/qr-visoesfilmes.png \
//             --texto visoesfilmes.com --pai <pid da Cabine>
//
// Sai sozinho se a Cabine morrer (--pai). Se o projetor sumir, esconde e volta
// quando ele voltar.
import AppKit

var opcoes: [String: String] = [:]
var i = 1
let argv = CommandLine.arguments
while i < argv.count {
    if argv[i].hasPrefix("--") && i + 1 < argv.count {
        opcoes[String(argv[i].dropFirst(2))] = argv[i + 1]
        i += 2
    } else {
        i += 1
    }
}
let nomeTela = (opcoes["tela"] ?? "").lowercased()
let espelhar = opcoes["espelhar"] == "1"
let texto = opcoes["texto"] ?? "visoesfilmes.com"
let pai = Int32(opcoes["pai"] ?? "") ?? 0
guard let caminho = opcoes["img"], let imagemLida = NSImage(contentsOfFile: caminho) else {
    FileHandle.standardError.write("raizes-qr: sem imagem (--img)\n".data(using: .utf8)!)
    exit(2)
}

// o projetor: pelo nome que a Cabine usa; sem nome (ou sem achar), o primeiro que nao e o principal
func acharTela() -> NSScreen? {
    let telas = NSScreen.screens
    if !nomeTela.isEmpty, let t = telas.first(where: { $0.localizedName.lowercased().contains(nomeTela) }) {
        return t
    }
    return telas.count > 1 ? telas.first(where: { $0 != NSScreen.main && $0 != telas.first }) ?? telas.last : nil
}

// as medidas do #qr da projecao.html, em vh/vw da tela do projetor
final class Vista: NSView {
    var vh: CGFloat = 10.8
    var imagem = NSImage()
    var espelhar = false
    var texto = ""
    override var isFlipped: Bool { false }

    var lado: CGFloat { 13 * vh }          // o QR: 13vh
    var folga: CGFloat { 1 * vh }          // em volta, para a sombra do texto
    var linha: CGFloat { ceil(1.6 * vh * 1.3) }
    var vao: CGFloat { 0.8 * vh }
    var margem: CGFloat { 5 * vh }         // dos lados do QR, para o texto caber centrado

    var tamanho: NSSize {
        NSSize(width: lado + 2 * margem, height: folga + linha + vao + lado + folga)
    }

    override func draw(_ sujo: NSRect) {
        NSColor.clear.set()
        bounds.fill(using: .copy)
        guard let ctx = NSGraphicsContext.current else { return }
        ctx.saveGraphicsState()
        if espelhar {                      // o scaleX(-1) da pagina: em torno do centro do QR
            let t = NSAffineTransform()
            t.translateX(by: bounds.width, yBy: 0)
            t.scaleX(by: -1, yBy: 1)
            t.concat()
        }
        let r = NSRect(x: (bounds.width - lado) / 2, y: folga + linha + vao, width: lado, height: lado)
        NSColor.white.setFill()
        NSBezierPath(roundedRect: r, xRadius: vh, yRadius: vh).fill()
        ctx.imageInterpolation = .high
        imagem.draw(in: r.insetBy(dx: 0.02 * lado, dy: 0.02 * lado), from: .zero, operation: .sourceOver, fraction: 1)

        let sombra = NSShadow()
        sombra.shadowColor = .black
        sombra.shadowBlurRadius = 6
        sombra.shadowOffset = NSSize(width: 0, height: -1)
        let fonte = NSFont.systemFont(ofSize: 1.6 * vh)
        let s = NSAttributedString(string: texto, attributes: [
            .font: fonte, .foregroundColor: NSColor.white, .kern: 0.06 * 1.6 * vh, .shadow: sombra,
        ])
        let t = s.size()
        s.draw(at: NSPoint(x: (bounds.width - t.width) / 2, y: folga + (linha - t.height) / 2))
        ctx.restoreGraphicsState()
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)        // sem icone no Dock, nunca toma o foco

let vista = Vista(frame: .zero)
vista.imagem = imagemLida
vista.espelhar = espelhar
vista.texto = texto
let janela = NSPanel(contentRect: NSRect(x: 0, y: 0, width: 10, height: 10),
                     styleMask: [.borderless, .nonactivatingPanel], backing: .buffered, defer: false)
janela.isOpaque = false
janela.backgroundColor = .clear
janela.hasShadow = false
janela.ignoresMouseEvents = true           // clique passa direto
janela.hidesOnDeactivate = false
janela.isFloatingPanel = true             // (isto baixa o nivel para "flutuante": o nivel vem DEPOIS)
janela.becomesKeyOnlyIfNeeded = true
// acima de tudo no projetor: do espelho em tela cheia e tambem do video do QLab, que
// mostra a Odara no nivel do protetor de tela (1000) -- 26/09, era ele que cobria o QR
janela.level = NSWindow.Level(rawValue: NSWindow.Level.screenSaver.rawValue + 1)
janela.collectionBehavior = [.canJoinAllSpaces, .stationary, .fullScreenAuxiliary, .ignoresCycle]
janela.contentView = vista

var ultimoQuadro = NSRect.zero

func posicionar() {
    guard let tela = acharTela() else {
        if janela.isVisible { janela.orderOut(nil) }
        ultimoQuadro = .zero
        return
    }
    let f = tela.frame
    let vh = f.height / 100, vw = f.width / 100
    vista.vh = vh
    let tam = vista.tamanho
    // o QR a 3vw da borda e 4vh do chao; espelhado, no canto oposto
    let esquerdaDoQR = espelhar ? f.minX + 3 * vw : f.maxX - 3 * vw - vista.lado
    let quadro = NSRect(x: (esquerdaDoQR - vista.margem).rounded(),
                        y: (f.minY + 4 * vh - vista.folga).rounded(),
                        width: tam.width.rounded(), height: tam.height.rounded())
    if quadro != ultimoQuadro {
        janela.setFrame(quadro, display: true)
        vista.frame = NSRect(origin: .zero, size: quadro.size)
        vista.needsDisplay = true
        ultimoQuadro = quadro
    }
    janela.orderFrontRegardless()          // se o espelho reabrir, o QR volta para cima
}

posicionar()
Timer.scheduledTimer(withTimeInterval: 2.0, repeats: true) { _ in
    if pai > 0 && kill(pai, 0) != 0 && errno == ESRCH { exit(0) }   // a Cabine saiu: sai junto
    MainActor.assumeIsolated { posicionar() }
}
NotificationCenter.default.addObserver(forName: NSApplication.didChangeScreenParametersNotification,
                                       object: nil, queue: .main) { _ in MainActor.assumeIsolated { posicionar() } }
signal(SIGTERM) { _ in exit(0) }
app.run()
