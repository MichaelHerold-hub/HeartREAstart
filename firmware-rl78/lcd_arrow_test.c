/*
 * HeartREAstart - Pfeil-Testprogramm fuer Renesas YRPBRL78L12
 * ============================================================
 *
 * Zweck:
 *   Test der Richtungsanzeige auf dem Segment-LCD der
 *   Renesas Promotion Board YRPBRL78L12 (RL78/L12, R5F10RLC).
 *
 * Funktionen:
 *   1. Automatischer Testmodus: Die vier Pfeile
 *      (oben, unten, links, rechts) werden zyklisch
 *      fuer je 1 Sekunde angezeigt.
 *   2. UART-Modus: Empfaengt ein Zeichen und zeigt den
 *      entsprechenden Pfeil an:
 *        'u' oder 'U' -> Pfeil oben
 *        'd' oder 'D' -> Pfeil unten
 *        'l' oder 'L' -> Pfeil links
 *        'r' oder 'R' -> Pfeil rechts
 *        'c' oder 'C' -> Position korrekt (alle Pfeile aus)
 *
 * Entwicklungsumgebung:
 *   - Renesas e2 studio (kostenlos)
 *   - GCC fuer RL78 (CC-RL), kostenlos
 *   - Debuggen ueber den On-Chip-Debugger (OCD) des Boards
 *
 * WICHTIG - Segment-Mapping anpassen:
 *   Die exakten Segmentadressen des custom segment LCD
 *   auf dem YRPBRL78L12 muessen aus dem Schaltplan
 *   (RPBRL78L12 Renesas Promotion Board Schematics, Rev.1.00)
 *   bzw. dem User's Manual des Boards entnommen werden.
 *   Die Konstanten unter "SEGTXT-MAPPING (ANPASSEN)" sind
 *   als Platzhalter definiert und muessen an die tatsaechliche
 *   Belegung angepasst werden.
 *
 * Hinweis:
 *   Der RL78/L12 verfuegt ueber einen Segment-LCD-Controller
 *   (SEG LCD). Die Ansteuerung erfolgt ueber die Register
 *   des LCD-Controllers. Details siehe:
 *   - RL78/L12 User's Manual: Hardware (R01UH0200)
 *   - YRPBRL78L12 User's Manual
 */

#include <stdint.h>

/* ============================================================
 * SEGTXT-MAPPING (ANPASSEN)
 * ============================================================
 * Diese Konstanten definieren, welche LCD-Segmente fuer die
 * vier Pfeile verwendet werden. Sie muessen anhand des
 * Schaltplans / der Segment-Tabelle des YRPBRL78L12 angepasst
 * werden.
 *
 * Typischerweise:
 *   - SEG-Segment-Adresse (Register) fuer den Pfeil
 *   - Bit-Maske innerhalb dieses Registers
 *
 * Beispiel-Platzhalter (muessen ersetzt werden):
 *   Die tatsaechlichen Werte stehen im YRPBRL78L12 User's
 *   Manual bzw. im Schaltplan unter der Segment-Tabelle.
 * ============================================================ */

/* Platzhalter: Register-Adressen und Bit-Masken fuer die
 * vier Pfeile. Diese Werte MUESSEN aus dem Board-Schaltplan
 * bzw. der Segment-Tabelle des YRPBRL78L12 entnommen werden. */

/* Beispiel: 4 Pfeile als einzelne Segmente definieren.
 * Jeder Pfeil besteht typischerweise aus mehreren Segmenten
 * (z. B. Dreieck aus 2-3 Segmenten). Hier als vereinfachtes
 * Beispiel mit je einem Segment pro Pfeil definiert. */

typedef struct {
    volatile uint8_t *seg_reg;  /* Zeiger auf das Segment-Register */
    uint8_t          seg_mask;  /* Bit-Maske des Segments           */
} arrow_segment_t;

/* --- ANPASSEN: Registeradressen und Bitmasken fuer Pfeile ---
 * Beispiel-Platzhalter. Die echten Adressen koennen z. B. so
 * aussehen (fiktive Beispielwerte, muessen ersetzt werden):
 *   Pfeil oben    -> Register 0x0000, Bit 0x01
 *   Pfeil unten   -> Register 0x0000, Bit 0x02
 *   Pfeil links   -> Register 0x0000, Bit 0x04
 *   Pfeil rechts  -> Register 0x0000, Bit 0x08
 */
static volatile uint8_t *LCD_SEG_BASE = (volatile uint8_t *)0xF0080u; /* Beispiel */

static const arrow_segment_t ARROW_UP    = { (volatile uint8_t *)0xF0080u, 0x01u };
static const arrow_segment_t ARROW_DOWN  = { (volatile uint8_t *)0xF0080u, 0x02u };
static const arrow_segment_t ARROW_LEFT  = { (volatile uint8_t *)0xF0080u, 0x04u };
static const arrow_segment_t ARROW_RIGHT = { (volatile uint8_t *)0xF0080u, 0x08u };

/* ============================================================
 * LCD-CONTROLLER INITIALISIERUNG
 * ============================================================
 * Der RL78/L12 besitzt einen Segment-LCD-Controller.
 * Typische Konfiguration fuer das YRPBRL78L12:
 *   - LCD-Taktquelle: interne Oszillation (ca. 32.768 kHz
 *     oder Sub-Clock)
 *   - Bias: 1/3
 *   - Duty: 1/4
 *   - VLCD: intern erzeugt
 *
 * Die genaue Konfiguration entnehmt ihr dem YRPBRL78L12
 * User's Manual bzw. dem Beispielcode von Renesas.
 */

/* WICHTIG: Diese Registeradressen sind Beispiel-Platzhalter
 * und muessen an die tatsaechlichen Register des RL78/L12
 * angepasst werden. Siehe RL78/L12 User's Manual: Hardware
 * (R01UH0200), Kapitel Segment-LCD-Controller. */

/* Beispiel-Registerdefinitionen (muessen ueberprueft werden): */
#define LCD_MODE_REG        (*(volatile uint8_t *)0xFFFC8u)  /* LCDMD   */
#define LCD_CTRL_REG        (*(volatile uint8_t *)0xFFFC9u)  /* LCDC0   */
#define LCD_CLK_REG         (*(volatile uint8_t *)0xFFFCAu)  /* LCDC1   */
#define LCD_VOLT_REG        (*(volatile uint8_t *)0xFFFCBu)  /* VLCD    */

static void lcd_init(void)
{
    /* 1. LCD-Controller aktivieren
     *    (Konfiguration anhand des Board-Handbuchs anpassen)
     */
    /* Beispiel:
     * LCD_MODE_REG = 0x00u;   Modus setzen
     * LCD_CLK_REG  = 0x03u;   Taktquelle waehlen
     * LCD_CTRL_REG = 0x07u;   Duty/Bias konfigurieren
     * LCD_VOLT_REG = 0x03u;   VLCD-Spannung setzen
     */

    /* 2. Alle Segmente ausschalten */
    for (uint8_t i = 0; i < 8; i++) {
        LCD_SEG_BASE[i] = 0x00u;
    }
}

static void lcd_clear_all(void)
{
    for (uint8_t i = 0; i < 8; i++) {
        LCD_SEG_BASE[i] = 0x00u;
    }
}

static void lcd_show_arrow(const arrow_segment_t *arrow)
{
    lcd_clear_all();
    *(arrow->seg_reg) |= arrow->seg_mask;
}

/* ============================================================
 * UART-INITIALISIERUNG
 * ============================================================
 * UART fuer Empfang von Richtungskommandos vom Raspberry Pi.
 * Baudrate: 9600, 8N1
 *
 * Der RL78/L12 verfuegt ueber UART (SCI).
 * Die Pinbelegung entnehmt ihr dem YRPBRL78L12 User's Manual.
 */

/* Beispiel-Register fuer UART (muessen angepasst werden): */
#define UART_CTRL_REG        (*(volatile uint8_t *)0xFFFF00u)
#define UART_BAUD_REG        (*(volatile uint8_t *)0xFFFF01u)
#define UART_STATUS_REG      (*(volatile uint8_t *)0xFFFF02u)
#define UART_RX_DATA_REG     (*(volatile uint8_t *)0xFFFF03u)

static void uart_init(void)
{
    /* Beispiel:
     * UART_CTRL_REG = 0x00u;   UART deaktivieren fuer Konfiguration
     * UART_BAUD_REG = 0x19u;   Baudrate 9600 bei angenommener Taktfrequenz
     * UART_CTRL_REG = 0x80u;   UART aktivieren, Empfang aktivieren
     */
}

static uint8_t uart_receive(void)
{
    /* Beispiel: Warten bis Empfangspuffer gefuellt, dann lesen.
     * Die genaue Implementierung haengt vom gewaehlten
     * Betriebsmodus (Polling/Interrupt) ab.
     */
    if (UART_STATUS_REG & 0x40u) {  /* Empfangspuffer voll? */
        return UART_RX_DATA_REG;
    }
    return 0u;
}

/* ============================================================
 * HAUPTPROGRAMM
 * ============================================================ */

typedef enum {
    DIR_NONE = 0,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT
} direction_t;

static direction_t direction_from_char(uint8_t c)
{
    switch (c) {
        case 'u': case 'U': return DIR_UP;
        case 'd': case 'D': return DIR_DOWN;
        case 'l': case 'L': return DIR_LEFT;
        case 'r': case 'R': return DIR_RIGHT;
        case 'c': case 'C': return DIR_NONE;
        default:             return DIR_NONE;
    }
}

static void show_direction(direction_t dir)
{
    switch (dir) {
        case DIR_UP:    lcd_show_arrow(&ARROW_UP);    break;
        case DIR_DOWN:  lcd_show_arrow(&ARROW_DOWN);  break;
        case DIR_LEFT:  lcd_show_arrow(&ARROW_LEFT);  break;
        case DIR_RIGHT: lcd_show_arrow(&ARROW_RIGHT); break;
        case DIR_NONE:  lcd_clear_all();              break;
    }
}

/* Einfache Warteschleife fuer den automatischen Testmodus.
 * Bei 24 MHz ergibt eine Schleife von ca. 1.000.000
 * Iterationen grob 1 Sekunde (je nach Optimierung). */
static void delay_ms(uint32_t ms)
{
    volatile uint32_t counter = ms * 1000u;
    while (counter > 0u) {
        counter--;
    }
}

int main(void)
{
    /* Hardware initialisieren */
    lcd_init();
    uart_init();

    /* --- Automatischer Testmodus ---
     * Die vier Pfeile werden zyklisch fuer je 1 Sekunde
     * angezeigt. Danach alle aus fuer 1 Sekunde.
     */
    const direction_t test_sequence[] = {
        DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_NONE
    };
    const uint8_t test_count = sizeof(test_sequence) / sizeof(test_sequence[0]);
    uint8_t test_index = 0u;
    uint32_t test_timer = 0u;

    /* Zustandsmaschine: Nach 5 Zyklen Testmodus in den
     * UART-Modus wechseln. */
    uint8_t test_cycles_done = 0u;
    const uint8_t MAX_TEST_CYCLES = 3u;
    uint8_t in_uart_mode = 0u;

    direction_t current_dir = DIR_NONE;

    while (1) {
        if (!in_uart_mode) {
            /* --- Testmodus: Pfeile zyklisch anzeigen --- */
            show_direction(test_sequence[test_index]);
            delay_ms(1000u);

            test_index++;
            if (test_index >= test_count) {
                test_index = 0u;
                test_cycles_done++;

                if (test_cycles_done >= MAX_TEST_CYCLES) {
                    in_uart_mode = 1u;
                    lcd_clear_all();
                }
            }
        } else {
            /* --- UART-Modus: Auf Kommando warten --- */
            uint8_t rx = uart_receive();
            if (rx != 0u) {
                current_dir = direction_from_char(rx);
                show_direction(current_dir);
            }
            /* Kurze Pause, um die CPU-Last zu reduzieren */
            delay_ms(10u);
        }
    }

    /* Wird nie erreicht */
    return 0;
}
