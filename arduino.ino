#include <usbhid.h>
#include <hiduniversal.h>
#include <Usb.h>
#include <usbhub.h>
#include <hidboot.h>
#include <SPI.h>
#include <Ethernet.h>
#define led 4
USB Usb;
USBHub Hub(&Usb);
HIDUniversal Hid(&Usb);
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(169, 254, 158, 142);
EthernetServer server(80);

String msg = "";
bool flag = true;
uint32_t timeout;

class KbdRptParser : public KeyboardReportParser {
    void PrintKey(uint8_t mod, uint8_t key);
  protected:
    virtual void OnKeyDown  (uint8_t mod, uint8_t key);
    virtual void OnKeyPressed(uint8_t key);
};

void KbdRptParser::OnKeyDown(uint8_t mod, uint8_t key)
{
  uint8_t c = OemToAscii(mod, key);

  if (c)
    OnKeyPressed(c);
}

void KbdRptParser::OnKeyPressed(uint8_t key)
{
  timeout = millis() + 100;
  flag = false;
  msg += (char) key;
};

KbdRptParser Prs;

void setup()
{
  

  Ethernet.init(7);
  Serial.begin( 9600 );
  Serial.println("Start");
  

  if (Usb.Init() == -1) {
    Serial.println("OSC did not start.");
  }

  delay( 200 );

  Hid.SetReportParser(0, (HIDReportParser*)&Prs);
  // если не удалось сконфигурировать Ethernet при помощи DHCP
  Serial.println("Failed to configure Ethernet using DHCP");
  // продолжать дальше смысла нет, поэтому вместо DHCP
  // попытаемся сделать это при помощи IP-адреса:
  Ethernet.begin(mac, ip);
  server.begin();
  Serial.print("Server is at ");
  Serial.println(Ethernet.localIP());
  pinMode(led, OUTPUT);


}

void loop()
{
  EthernetClient client = server.available();
  Usb.Task();
  if (millis() > timeout && flag == false ) {
    flag = true;
    Serial.println(msg);
    digitalWrite(led, HIGH);
    delay(2000);
    digitalWrite(led, LOW);
    Serial.println("new client");
    // HTTP-запрос заканчивается пустой линией
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.write(c);
        if (c == '\n' && currentLineIsBlank) {
          // отсылаем стандартный заголовок для HTTP-ответа:
          client.println("HTTP/1.1 200 OK");
          client.println("Refresh:1");
          client.println("Content-Type: text/html");
          // после выполнения ответа соединение будет разорвано
          client.println("Connection: close");
          // автоматически обновляем страницу каждые 5 секунд
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");
          // выводим значения ото всех входных аналоговых контактов:
          client.println(msg);

          client.println("</html>");

          break;
        }
        if (c == '\n') {
          // начинаем новую строку
          currentLineIsBlank = true;
        } else if (c != '\r') {
          // в текущей строке есть символ:
          currentLineIsBlank = false;
        }
      }
    }
    // даем браузеру время, чтобы получить данные
    delay(1);
    // закрываем соединение
    client.stop();
    msg = "";
    // клиент отключился
    Serial.println("Client disconnected");
  }
}
