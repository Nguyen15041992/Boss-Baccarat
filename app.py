import SwiftUI

@main
struct BossBaccaratApp: App { var body: some Scene { WindowGroup { ContentView() } } }

struct Round: Identifiable, Codable, Equatable { let id: UUID; let value: String; init(value: String){ id=UUID(); self.value=value } }
struct PredictionRecord: Identifiable, Codable { let id: UUID; let prediction: String; let createdAfterRound: Int; var actual: String?; var correct: Bool?; init(prediction:String,createdAfterRound:Int){id=UUID();self.prediction=prediction;self.createdAfterRound=createdAfterRound} }

@MainActor final class BaccaratStore: ObservableObject {
 @Published var rounds:[Round]=[]; @Published var records:[PredictionRecord]=[]
 init(){load()}
 func add(_ value:String){
  if let i=records.lastIndex(where:{$0.actual == nil}), value != "T" { records[i].actual=value; records[i].correct=(records[i].prediction == value) }
  rounds.append(Round(value:value)); makePrediction(); save()
 }
 func undo(){ guard !rounds.isEmpty else{return}; rounds.removeLast(); if !records.isEmpty{records.removeLast()}; save() }
 func reset(){rounds.removeAll();records.removeAll();save()}
 func currentPrediction()->Analysis?{ Analyzer.analyze(rounds.map(\.value)) }
 private func makePrediction(){ if let a=currentPrediction(){records.append(PredictionRecord(prediction:a.prediction,createdAfterRound:rounds.count))} }
 var accuracy:Int?{let d=records.compactMap(\.correct);guard !d.isEmpty else{return nil};return Int((Double(d.filter{$0}.count)/Double(d.count)*100).rounded())}
 private func save(){let d=UserDefaults.standard;d.set(try? JSONEncoder().encode(rounds),forKey:"boss.rounds");d.set(try? JSONEncoder().encode(records),forKey:"boss.records")}
 private func load(){let d=UserDefaults.standard;if let x=d.data(forKey:"boss.rounds"),let v=try? JSONDecoder().decode([Round].self,from:x){rounds=v};if let x=d.data(forKey:"boss.records"),let v=try? JSONDecoder().decode([PredictionRecord].self,from:x){records=v}}
}

struct Analysis { let prediction:String; let confidence:Int; let pScore:Double; let bScore:Double; let tieRate:Int; let pattern:String; let reasons:[String]; let signals:[String] }

enum Analyzer {
 struct Run {let value:String;let count:Int}
 static func analyze(_ raw:[String])->Analysis? {
  let a=raw.filter{$0=="P" || $0=="B"}; guard a.count>=6 else{return nil}
  var p=50.0,b=50.0,reasons:[String]=[],signals:[String]=[]
  let rs=runs(a), last=a.last!
  if let r=rs.last,r.count>=2 { if r.value=="P"{p+=18;reasons.append("Cầu bệt P × \(r.count)")}else{b+=18;reasons.append("Cầu bệt B × \(r.count)")};signals.append("Bệt") }
  let alt=alternatingTail(a); if alt>=4 {if last=="P"{b+=15}else{p+=15};reasons.append("Cầu 1–1 / xen kẽ \(alt) ván");signals.append("Xen kẽ")}
  if rs.count>=4 {let x=Array(rs.suffix(4).map(\.count));if Set(x).count==1 && x[0] <= 5 {if last=="P"{b+=14}else{p+=14};reasons.append("Cầu \(x[0])-\(x[0])-\(x[0])-\(x[0])");signals.append("Cụm đều")}}
  if let x=detectBlockPattern(rs){if last=="P"{b+=12}else{p+=12};reasons.append(x);signals.append("Cầu cụm")}
  addFrequency(Array(a.suffix(8)),weight:16,p:&p,b:&b); addFrequency(Array(a.suffix(20)),weight:12,p:&p,b:&b)
  let k=min(5,a.count-1), motif=Array(a.suffix(k)); var fp=0,fb=0
  if a.count>k {for i in k..<a.count {if Array(a[(i-k)..<i])==motif {if a[i]=="P"{fp+=1}else{fb+=1}}}}
  if fp+fb>=2 {if fp>fb{p+=15}else if fb>fp{b+=15};reasons.append("Mẫu \(k) ván lặp: \(fp) P / \(fb) B");signals.append("Mẫu lặp")}
  if let r=rs.last,r.count>=3 { if r.count>=5 { if last=="P"{b+=7}else{p+=7};reasons.append("Cảnh báo cuối chuỗi bệt dài");signals.append("Nguy cơ gãy") } }
  let pc=a.filter{$0=="P"}.count,bc=a.count-pc,diff=abs(p-b)
  let pred = diff < 8 ? "KHÔNG RÕ" : (p>b ? "PLAYER" : "BANKER")
  let conf=min(92,max(50,Int((50+diff*1.55).rounded())))
  let tie=raw.isEmpty ? 0 : Int((Double(raw.filter{$0=="T"}.count)/Double(raw.count)*100).rounded())
  let pattern=rs.suffix(8).map{"\($0.value)\($0.count)"}.joined(separator:"  ")
  var rr=reasons; if rr.isEmpty{rr.append("Chưa có cầu đủ mạnh")}; rr.append("Tổng mẫu P=\(pc), B=\(bc)")
  return Analysis(prediction:pred,confidence:conf,pScore:p,bScore:b,tieRate:tie,pattern:pattern,reasons:rr,signals:Array(Set(signals)).sorted())
 }
 static func addFrequency(_ a:[String],weight:Double,p:inout Double,b:inout Double){guard !a.isEmpty else{return};let pc=Double(a.filter{$0=="P"}.count),bc=Double(a.filter{$0=="B"}.count);if pc>bc{p+=(pc-bc)/Double(a.count)*weight};if bc>pc{b+=(bc-pc)/Double(a.count)*weight}}
 static func runs(_ a:[String])->[Run]{guard let f=a.first else{return[]};var o:[Run]=[],v=f,n=1;for x in a.dropFirst(){if x==v{n+=1}else{o.append(Run(value:v,count:n));v=x;n=1}};o.append(Run(value:v,count:n));return o}
 static func alternatingTail(_ a:[String])->Int{guard a.count>1 else{return a.count};var n=1;for i in stride(from:a.count-1,through:1,by:-1){if a[i] != a[i-1]{n+=1}else{break}};return n}
 static func detectBlockPattern(_ rs:[Run])->String?{guard rs.count>=6 else{return nil};let x=Array(rs.suffix(6).map(\.count));if x[0]==x[2] && x[2]==x[4] && x[1]==x[3] && x[3]==x[5] {return "Cầu nhịp \(x[0])-\(x[1]) lặp"};return nil}
}

struct ContentView: View {
 @StateObject private var store=BaccaratStore(); var analysis:Analysis?{store.currentPrediction()}; var counts:(Int,Int,Int){(store.rounds.filter{$0.value=="P"}.count,store.rounds.filter{$0.value=="B"}.count,store.rounds.filter{$0.value=="T"}.count)}
 var body:some View{ZStack{Color(.systemGroupedBackground).ignoresSafeArea();ScrollView{VStack(spacing:14){Text("BOSS BACCARAT").font(.system(size:32,weight:.black));Text("V5 • NHẬN DIỆN NHIỀU CẦU").font(.caption.bold()).foregroundStyle(.secondary);predictionCard;inputCard;signalsCard;analysisCard;statsCard;historyCard;HStack{Button("↩ Hoàn tác"){store.undo()}.buttonStyle(.bordered);Spacer();Button("Xóa dữ liệu",role:.destructive){store.reset()}.buttonStyle(.bordered)};Text("Phân tích thống kê không thể bảo đảm kết quả ván Baccarat tiếp theo.").font(.footnote).foregroundStyle(.secondary).multilineTextAlignment(.center)}.padding()}}}
 var predictionCard:some View{VStack(spacing:8){Text("DỰ ĐOÁN VÁN TIẾP THEO").font(.caption.bold()).foregroundStyle(.secondary);Text(analysis?.prediction ?? "CHƯA ĐỦ DỮ LIỆU").font(.system(size:34,weight:.black));Text(analysis.map{"Độ mạnh tín hiệu \($0.confidence)%"} ?? "Cần ít nhất 6 ván P/B").foregroundStyle(.secondary);ProgressView(value:Double(analysis?.confidence ?? 0),total:100)}.padding(20).frame(maxWidth:.infinity).background(.regularMaterial).clipShape(RoundedRectangle(cornerRadius:24))}
 var inputCard:some View{HStack{input("PLAYER","P",.red);input("BANKER","B",.blue);input("TIE","T",.gray)}}
 func input(_ t:String,_ v:String,_ c:Color)->some View{Button{store.add(v)}label:{Text(t).font(.headline.bold()).frame(maxWidth:.infinity).padding(.vertical,15)}.buttonStyle(.borderedProminent).tint(c)}
 var signalsCard:some View{VStack(alignment:.leading,spacing:8){Text("🧠 CÁC CẦU ĐANG NHẬN DIỆN").font(.headline.bold());if let a=analysis,!a.signals.isEmpty{LazyVGrid(columns:[GridItem(.flexible()),GridItem(.flexible())]){ForEach(a.signals,id:\.self){Text($0).frame(maxWidth:.infinity).padding(8).background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius:10))}}}else{Text("Chưa đủ dữ liệu").foregroundStyle(.secondary)}}.padding().frame(maxWidth:.infinity,alignment:.leading).background(.regularMaterial).clipShape(RoundedRectangle(cornerRadius:18))}
 var analysisCard:some View{VStack(alignment:.leading,spacing:9){Text("🔎 CHI TIẾT PHÂN TÍCH").font(.headline.bold());if let a=analysis{Text("Cầu hiện tại: \(a.pattern)");Text("Điểm PLAYER: \(a.pScore,specifier:"%.1f")");Text("Điểm BANKER: \(a.bScore,specifier:"%.1f")");Text("Tỷ lệ Hòa lịch sử: \(a.tieRate)%");Divider();ForEach(a.reasons,id:\.self){Text("• \($0)").fontWeight(.semibold)}}else{Text("Nhập thêm kết quả để Boss phân tích.").foregroundStyle(.secondary)}}.padding().frame(maxWidth:.infinity,alignment:.leading).background(.regularMaterial).clipShape(RoundedRectangle(cornerRadius:18))}
 var statsCard:some View{HStack{stat("P",counts.0,.red);stat("B",counts.1,.blue);stat("T",counts.2,.gray);stat("ĐÚNG",store.accuracy.map{"\($0)%"} ?? "—",.green)}.padding().background(.regularMaterial).clipShape(RoundedRectangle(cornerRadius:18))}
 func stat(_ l:String,_ v:Any,_ c:Color)->some View{VStack{Text("\(v)").font(.title3.bold()).foregroundStyle(c);Text(l).font(.caption2).foregroundStyle(.secondary)}.frame(maxWidth:.infinity)}
 var historyCard:some View{VStack(alignment:.leading){Text("🎴 LỊCH SỬ • \(store.rounds.count) VÁN").font(.headline.bold());LazyVGrid(columns:Array(repeating:GridItem(.flexible()),count:10),spacing:7){ForEach(store.rounds){r in Text(r.value).font(.caption.bold()).foregroundStyle(.white).frame(width:30,height:30).background(color(r.value)).clipShape(Circle())}}}.padding().frame(maxWidth:.infinity,alignment:.leading).background(.regularMaterial).clipShape(RoundedRectangle(cornerRadius:18))}
 func color(_ x:String)->Color{x=="P" ? .red : x=="B" ? .blue : .gray}
}
