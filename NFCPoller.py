class NFCPoller:
    def __init__(self, nfc_adapter):
        self.nfc_adapter = nfc_adapter
        self.current_tag = None

    def poll(self):
        # Start polling for NFC tags
        print("Starting NFC polling...")
        
        #Code here to set a tag to the value seen by the hardware
        tag = "12345ABD"
        if tag and tag != self.current_tag:
            # New tag detected
            self.current_tag = tag
            print(f"Tag detected: {tag}")
            
        return tag

if __name__ == "__main__":
  nfc = NFCPoller("Test")
  nfc.poll()
