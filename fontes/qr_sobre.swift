// O QR POR CIMA DO ESPELHO (26/09). "O QR code nao esta aparecendo."
//
// Com o oculos na cabeca o projetor mostra o espelho do Quest (scrcpy, em tela
// cheia, num Space proprio do macOS) -- e o QR so existia na pagina da animacao,
// que fica por baixo. Este programinha poe o QR numa janela sem borda, que nao
// recebe clique nem foco, acima de tudo e em todos os Spaces do projetor: a troca
// espelho <-> animacao nao mexe o QR. Em retroprojecao (--espelhar 1) vai para o
// outro canto e sai invertido, para quem olha do outro lado do tule le-lo certo.
//
// TRES QR (27/09): "faz um QR code da versao mobile pra pessoa acessar o nosso site,
// do lado do QR code do site e do Instagram, sao 3. Mas faz uma diferenciacao e nao
// precisa ficar tao grande." Se ao lado da imagem (--img) houver um qr_sobre.json,
// ele manda: uma fileira de cartoes menores, cada um com a borda e o rotulo na sua
// cor. Sem o arquivo, fica o QR unico de antes.
//
// 27/09, depois: "o texto embaixo nao da pra ver, coloca centralizado embaixo". No canto e
// colada na borda de baixo, a fileira caia onde o tule ja nao pega. Agora ela vai ao centro
// ("posicao": "centro"), mais alta ("baixo_vh"), e cada rotulo e maior e vem sobre uma
// faixa escura, centralizado sob o seu QR.
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
let pai = Int32(opcoes["pai"] ?? "") ?? 0

struct Cartao {
    let imagem: NSImage
    let rotulo: String
    let cor: NSColor
}

func corDe(_ hex: String) -> NSColor {
    var h = hex.trimmingCharacters(in: .whitespaces)
    if h.hasPrefix("#") { h.removeFirst() }
    guard h.count == 6, let v = UInt32(h, radix: 16) else { return .white }
    return NSColor(srgbRed: CGFloat((v >> 16) & 255) / 255, green: CGFloat((v >> 8) & 255) / 255,
                   blue: CGFloat(v & 255) / 255, alpha: 1)
}

// os cartoes: do qr_sobre.json ao lado da imagem, ou o QR unico do --img
guard let caminho = opcoes["img"] else {
    FileHandle.standardError.write("raizes-qr: sem imagem (--img)\n".data(using: .utf8)!)
    exit(2)
}
let pasta = URL(fileURLWithPath: caminho).deletingLastPathComponent()
var cartoes: [Cartao] = []
var ladoVh: CGFloat = 13
var noCentro = false
var baixoVh: CGFloat = 4
if let dados = try? Data(contentsOf: pasta.appendingPathComponent("qr_sobre.json")),
   let json = try? JSONSerialization.jsonObject(with: dados) as? [String: Any],
   let itens = json["itens"] as? [[String: Any]] {
    for it in itens {
        guard let img = it["img"] as? String,
              let im = NSImage(contentsOf: pasta.appendingPathComponent(img)) else { continue }
        cartoes.append(Cartao(imagem: im, rotulo: it["rotulo"] as? String ?? "", cor: corDe(it["cor"] as? String ?? "#ffffff")))
    }
    if let l = json["lado_vh"] as? Double { ladoVh = CGFloat(l) }
    noCentro = (json["posicao"] as? String) == "centro"
    if let b = json["baixo_vh"] as? Double { baixoVh = CGFloat(b) }
}
if cartoes.isEmpty {
    guard let im = NSImage(contentsOfFile: caminho) else {
        FileHandle.standardError.write("raizes-qr: imagem ilegivel (--img)\n".data(using: .utf8)!)
        exit(2)
    }
    cartoes = [Cartao(imagem: im, rotulo: opcoes["texto"] ?? "visoesfilmes.com", cor: .white)]
    ladoVh = 13
}

// o projetor: pelo nome que a Cabine usa; sem nome (ou sem achar), o primeiro que nao e o principal
func acharTela() -> NSScreen? {
    let telas = NSScreen.screens
    if !nomeTela.isEmpty, let t = telas.first(where: { $0.localizedName.lowercased().contains(nomeTela) }) {
        return t
    }
    return telas.count > 1 ? telas.first(where: { $0 != NSScreen.main && $0 != telas.first }) ?? telas.last : nil
}

// as medidas em vh da tela do projetor
final class Vista: NSView {
    var vh: CGFloat = 10.8
    var cartoes: [Cartao] = []
    var espelhar = false
    var ladoVh: CGFloat = 13
    override var isFlipped: Bool { false }

    var lado: CGFloat { ladoVh * vh }                          // cada QR
    var folga: CGFloat { 1 * vh }                              // em volta, para a sombra do texto
    var corpo: CGFloat { (cartoes.count > 1 ? 2.0 : 1.6) * vh }    // a letra do rotulo
    var linha: CGFloat { ceil(corpo * 1.3) + (cartoes.count > 1 ? 0.9 * vh : 0) }   // e a faixa escura dele
    var vao: CGFloat { 0.6 * vh }                              // entre o QR e o rotulo
    var entre: CGFloat { 2.4 * vh }                            // entre um cartao e outro

    func textoDe(_ c: Cartao) -> NSAttributedString {
        let sombra = NSShadow()
        sombra.shadowColor = .black
        sombra.shadowBlurRadius = 6
        sombra.shadowOffset = NSSize(width: 0, height: -1)
        return NSAttributedString(string: c.rotulo, attributes: [
            .font: NSFont.systemFont(ofSize: corpo, weight: .semibold), .foregroundColor: c.cor,
            .kern: 0.04 * corpo, .shadow: sombra,
        ])
    }
    // cada cartao ocupa a largura do maior entre o QR e o rotulo (com a faixa): espacados por igual
    var vaga: CGFloat { max(lado, (cartoes.map { textoDe($0).size().width }.max() ?? 0) + (cartoes.count > 1 ? 1.8 * vh : 0)) }
    var larguraDaFileira: CGFloat { CGFloat(cartoes.count) * vaga + CGFloat(max(0, cartoes.count - 1)) * entre }
    var tamanho: NSSize {
        NSSize(width: larguraDaFileira + 2 * folga, height: folga + linha + vao + lado + folga)
    }

    override func draw(_ sujo: NSRect) {
        NSColor.clear.set()
        bounds.fill(using: .copy)
        guard let ctx = NSGraphicsContext.current else { return }
        ctx.saveGraphicsState()
        if espelhar {                      // o scaleX(-1) da pagina: a fileira inteira, invertida
            let t = NSAffineTransform()
            t.translateX(by: bounds.width, yBy: 0)
            t.scaleX(by: -1, yBy: 1)
            t.concat()
        }
        ctx.imageInterpolation = .high
        for (k, c) in cartoes.enumerated() {
            let x0 = folga + CGFloat(k) * (vaga + entre)
            let r = NSRect(x: (x0 + (vaga - lado) / 2).rounded(), y: (folga + linha + vao).rounded(),
                           width: lado.rounded(), height: lado.rounded())
            let caixa = NSBezierPath(roundedRect: r, xRadius: 0.8 * vh, yRadius: 0.8 * vh)
            NSColor.white.setFill()
            caixa.fill()
            /* NITIDO (27/09, "o QR da obra esta sendo dificil de ler"): cada modulo com um numero
               inteiro de pixels do projetor e sem suavizar -- borda borrada a camera do celular nao
               le no tule. A imagem ja vem com 1 pixel por modulo e os 4 de margem branca. */
            let px = CGFloat(c.imagem.representations.first?.pixelsWide ?? 0)
            let k = px > 0 ? floor(r.width / px) : 0
            if k >= 1 {
                let lq = k * px
                let q = NSRect(x: r.minX + ((r.width - lq) / 2).rounded(), y: r.minY + ((r.height - lq) / 2).rounded(), width: lq, height: lq)
                ctx.imageInterpolation = .none
                c.imagem.draw(in: q, from: .zero, operation: .sourceOver, fraction: 1)
            } else {
                ctx.imageInterpolation = .high
                c.imagem.draw(in: r.insetBy(dx: 0.05 * lado, dy: 0.05 * lado), from: .zero, operation: .sourceOver, fraction: 1)
            }
            if cartoes.count > 1 {         // a diferenca de cada um: a borda na cor dele
                c.cor.setStroke()
                caixa.lineWidth = 0.32 * vh
                caixa.stroke()
            }
            let s = textoDe(c)
            let t = s.size()
            if cartoes.count > 1 {         // a faixa escura por tras da letra: se le sobre o video claro
                let fx = NSRect(x: x0 + (vaga - t.width) / 2 - 0.9 * vh, y: folga, width: t.width + 1.8 * vh, height: linha)
                NSColor(calibratedWhite: 0, alpha: 0.62).setFill()
                NSBezierPath(roundedRect: fx, xRadius: linha / 2, yRadius: linha / 2).fill()
            }
            s.draw(at: NSPoint(x: x0 + (vaga - t.width) / 2, y: folga + (linha - t.height) / 2))
        }
        ctx.restoreGraphicsState()
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.accessory)        // sem icone no Dock, nunca toma o foco

let vista = Vista(frame: .zero)
vista.cartoes = cartoes
vista.espelhar = espelhar
vista.ladoVh = ladoVh
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
    // no centro (27/09), ou a 3vw da borda (espelhada, no canto oposto); baixoVh acima do chao
    let esquerda = noCentro ? f.midX - vista.larguraDaFileira / 2
                 : (espelhar ? f.minX + 3 * vw : f.maxX - 3 * vw - vista.larguraDaFileira)
    let quadro = NSRect(x: (esquerda - vista.folga).rounded(),
                        y: (f.minY + baixoVh * vh - vista.folga).rounded(),
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
