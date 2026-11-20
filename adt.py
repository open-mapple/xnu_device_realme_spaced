# The realme 8i's device tree values, for build/mapple/tools/mkadt.py (with tools/soc/mt6781.py).

# 4 GB of RAM, 0x40000000-0x13fffffff; LK's reservations are all below 0xc0000000 but for dramc-rk at 0x13ffff000, so
# XNU gets 0xc0000000 up to the 32 MB boundary below it: (base, size).
RAM = (0xc0000000, 0x13e000000 - 0xc0000000)
# LK's framebuffer: atag,videolfb 0x771b0000, the first of three 1080x2412 buffers, pitch 4320.
FB = dict(base=0x771b0000, width=1080, height=2412, stride=1080 * 4)
FB['size'] = (FB['stride'] * FB['height'] + 0x3fff) & ~0x3fff
ECID = 0x5350414300000001  # 'SPAC' + 1, synthetic
PRODUCT_NAME = 'realme 8i'
DISPLAY_GAMUT = 'sRGB'    # the panel is shown as 8-bit BGRA
# About: serial-number is a placeholder the shim overwrites at each boot with LK's androidboot.serialno.
ABOUT = dict(serial='MAPPLE0000000000', model='RMX3151', region='', regulatory='RMX3151')


def devices(a, ph, phandle, gic_ph, ecid, flags):
    """/arm-io devices: viva's MT6781 blocks, its own keys and touch screen; nothing for chips it lacks."""
    node, cstr, u32, spi, io, wifi_mac = a.node, a.cstr, a.u32, a.spi, a.io, a.wifi_mac
    IRQ_EDGE_RISING, IRQ_EDGE_FALLING, IRQ_LEVEL_HIGH = a.IRQ_EDGE_RISING, a.IRQ_EDGE_FALLING, a.IRQ_LEVEL_HIGH
    HID_CSMR_POWER, HID_CSMR_VOLUME_UP, HID_CSMR_VOLUME_DOWN = a.HID_CSMR_POWER, a.HID_CSMR_VOLUME_UP, a.HID_CSMR_VOLUME_DOWN
    audio, torch, camera = flags['audio'], flags['torch'], flags['camera']
    eint_ph = next(phandle)
    return [
        # Volume down is bit 1 of KP_MEM1 here (kpd-hw-init-map 0x72); power and volume up are the PMIC's keys.
        node('keypad', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-keypad')),
            ('reg', io(0x10010000, 0x1000)),
            ('interrupt-parent', u32(gic_ph)),
            ('interrupts', spi(0x49, IRQ_EDGE_RISING)),
            ('keymap', u32(1, HID_CSMR_VOLUME_DOWN)),
        ]),
        node('eint', [
            ('AAPL,phandle', u32(eint_ph)),
            ('compatible', cstr('mediatek,mt6781-eint')),
            ('reg', io(0x1000b000, 0x1000)),
            ('interrupt-controller', b''),
            ('#interrupt-cells', u32(2)),
            ('interrupt-parent', u32(gic_ph)),
            ('interrupts', spi(0xba, IRQ_LEVEL_HIGH)),
        ]),
        # The PMIC (MT6358 family, the live DT's mt6358-pmic, interrupt EINT 144): key 0 PWRKEY = power,
        # 1 HOMEKEY = volume up (TOPSTATUS bits 1 and 3).
        node('pwrap', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-pwrap')),
            ('reg', io(0x1000d000, 0x1000)),
        ], [node('pmic', [
            ph(),
            ('compatible', cstr('mediatek,mt6366-pmic')),
            ('interrupt-parent', u32(eint_ph)),
            ('interrupts', u32(144, IRQ_LEVEL_HIGH)),
        ], [node('keys', [
            ph(),
            ('compatible', cstr('mediatek,mt6366-keys')),
            ('keymap', u32(0, HID_CSMR_POWER, 1, HID_CSMR_VOLUME_UP)),
        ])])]),
        # GPIO: only the touch screen's SPI4 pins driven by hand (MOSI 13, CLK 144, CS 145; MISO 14 is an input);
        # with --audio the speaker amplifier's enable / one-wire pin too (164, bsd/dev/mtk_audio.c).
        node('gpio', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-gpio')),
            ('reg', io(0x10005000, 0x1000)),
            ('output-pins', u32(13, 144, 145, *((164,) if audio else ()))),
        ]),
    ] + ([
        # --audio: I2C3 for the speaker amplifier (AW87319 0x58 or SIA8109 0x28, the live DT's aw87319 / sia81xx-i2c);
        # the controller as on viva (same SoC), no children: bsd/dev/mtk_audio.c talks to it by bus number.
        node('i2c3', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-i2c')),
            ('reg', io(0x1100f000, 0x1000) + io(0x11017000, 0x1000)),
            ('interrupt-parent', u32(gic_ph)),
            ('interrupts', spi(0x6c, IRQ_LEVEL_HIGH)),
            ('bus-id', u32(3)),
            ('imp-cg-bit', u32(3)),
            ('clock-frequency', u32(400000)),
            ('source-clock', u32(124800000)),
            ('clock-div', u32(5)),
            ('ext-time-config', u32(0x1801)),
        ]),
    ] if audio else []) + ([
        # --torch: I2C5 for the flash LED's chip (MT6371 PMU at 0x34, also the charger and the backlight;
        # bsd/dev/mtk_torch.c talks to it by bus number); the live DT's i2c5: SPI 354, gate bit 5, clock-div 5.
        node('i2c5', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-i2c')),
            ('reg', io(0x11016000, 0x1000) + io(0x11017000, 0x1000)),
            ('interrupt-parent', u32(gic_ph)),
            ('interrupts', spi(0x162, IRQ_LEVEL_HIGH)),
            ('bus-id', u32(5)),
            ('imp-cg-bit', u32(5)),
            ('clock-frequency', u32(400000)),
            ('source-clock', u32(124800000)),
            ('clock-div', u32(5)),
            ('ext-time-config', u32(0x1801)),
        ]),
    ] if torch else []) + ([
        # --camera: libMobileGestalt's rear-facing-camera and still-camera are /arm-io/isp's camera-rear (any value);
        # the camera itself is mapple-captured's.
        node('isp', [ph(), ('camera-rear', u32(1))]),
    ] + [
        # and the camera's buses (bsd/dev/mtk_cam.c, by bus number): I2C2 for its LDO chip (0x29), I2C4 for the rear
        # sensor, its VCM and EEPROM; the live DT's i2c2 SPI 107 and i2c4 SPI 109, gate bits 2 and 4, clock-div 5.
        node(f'i2c{n}', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-i2c')),
            ('reg', io(base, 0x1000) + io(0x11017000, 0x1000)),
            ('interrupt-parent', u32(gic_ph)),
            ('interrupts', spi(irq, IRQ_LEVEL_HIGH)),
            ('bus-id', u32(n)),
            ('imp-cg-bit', u32(n)),
            ('clock-frequency', u32(400000)),
            ('source-clock', u32(124800000)),
            ('clock-div', u32(5)),
            ('ext-time-config', u32(0x1801)),
        ]) for n, base, irq in ((2, 0x11009000, 107), (4, 0x11011000, 109))
    ] if camera else []) + [
        # ILI7807S touch (iokit/Kernel/arm/hid/ILI7807S.cpp): SPI4's pins by hand, a report per low pulse on
        # EINT 12; firmware sent by mtkloader before the shim (mp_ili_fw= for sending it again).
        node('touch', [
            ph(),
            ('compatible', cstr('ilitek,ili7807s')),
            ('spi-gpios', u32(13, 14, 144, 145)),
            ('interrupt-parent', u32(eint_ph)),
            ('interrupts', u32(12, IRQ_EDGE_FALLING)),
            ('max-x', u32(2047)),
            ('max-y', u32(2047)),
            ('panel-size', u32(FB['width'], FB['height'])),
        ]),
        # Mali-G57 MC2, the same SoC block as viva's (realme dts: mali@13000000, SPI 274-276): MappleGPU.cpp, which does
        # nothing without the boot-arg mp_gpu=1|2.
        node('gpu', [
            ph(),
            ('compatible', cstr('mediatek,mt6781-mali')),
            ('reg', io(0x13000000, 0x4000) + io(0x13fbf000, 0x1000) + io(0x10006000, 0x1000) +
                    io(0x10000000, 0x1000) + io(0x1000c000, 0x1000) + io(0x10001000, 0x1000)),
            ('interrupt-parent', u32(gic_ph)),
            ('interrupts', spi(0x112, IRQ_LEVEL_HIGH) + spi(0x113, IRQ_LEVEL_HIGH) + spi(0x114, IRQ_LEVEL_HIGH)),
        ]),
        # CONNSYS WiFi, as viva's: MT6631WLAN.cpp matches it; launchd starts wifid only with a node named "wlan".
        # wifi-vendor: MT6631WLAN.cpp publishes it as MobileGestalt's WifiVendor; BlueTool's built-in script for
        # this platform is only there for "Murata" and "USI" modules (the MT6631 has none of either).
        node('wlan', [
            ph(),
            ('device_type', cstr('wlan')),
            ('compatible', cstr('mediatek,mt6781-wlan')),
            ('local-mac-address', wifi_mac(ecid)),
            ('wifi-vendor', cstr('Murata')),
        ]),
    ]


