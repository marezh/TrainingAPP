//
//  ContentView.swift
//  PersonalTrainer2
//
//  Created by Marko lazovic on 22.05.2024.
//

import SwiftUI
import AVFoundation

struct ContentView: View {
    @State private var repetitions = 0
    @State private var readyMessageSpoken = false
    private let synth = AVSpeechSynthesizer()
    
    var body: some View {
        VStack {
            Text("Repetitions: \(repetitions)")
                .font(.title)
                .padding()
            
            Spacer()
        }
        .onAppear {
            startPythonProcess()
        }
    }
    
    func startPythonProcess() {
        let process = Process()
        process.launchPath = "/usr/bin/python3"
        process.arguments = [Bundle.main.path(forResource: "pose_detection", ofType: "py") ?? ""]
        
        let outputPipe = Pipe()
        process.standardOutput = outputPipe
        
        outputPipe.fileHandleForReading.waitForDataInBackgroundAndNotify()
        NotificationCenter.default.addObserver(forName: .NSFileHandleDataAvailable, object: outputPipe.fileHandleForReading , queue: nil) {  notification -> Void in
            let output = outputPipe.fileHandleForReading.availableData
            if let data = String(data: output, encoding: .utf8) {
                handlePythonOutput(data)
            }
            outputPipe.fileHandleForReading.waitForDataInBackgroundAndNotify()
        }
        
        process.launch()
    }
    
    func handlePythonOutput(_ data: String) {
        guard !data.isEmpty else {
         
            return
        }
        
        guard let jsonData = data.data(using: .utf8) else {
            print("Failed to convert data")
            return
        }
        
        do {
            if let json = try JSONSerialization.jsonObject(with: jsonData, options: []) as? [String: Any],
               let count = json["count"] as? Int,
               let counting = json["counting"] as? Bool,
               let ready = json["ready"] as? Bool {
                DispatchQueue.main.async {
                    self.repetitions = count
                    
                    if ready && !self.readyMessageSpoken {
                        self.speakReadyMessage()
                        self.readyMessageSpoken = true
                    }
                    
                    if !counting {
                        self.speakFinalCount(count)
                    }
                }
            }
        } catch {
            print("Error parsing JSON: \(error)")
        }
    }
    
    func speakReadyMessage() {
        let utterance = AVSpeechUtterance(string: "Okay, ich bin startklar")
        utterance.voice = AVSpeechSynthesisVoice(language: "de-DE")
        synth.speak(utterance)
    }
    
    func speakFinalCount(_ count: Int) {
        let utterance = AVSpeechUtterance(string: "Du hast \(count) Wiederholungen geschafft.")
        utterance.voice = AVSpeechSynthesisVoice(language: "de-DE")
        synth.speak(utterance)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

