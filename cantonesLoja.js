// ============================================================================
// ARCHIVO: cantonesLoja.js
// CAPA POLIGONAL DE ORDENAMIENTO TERRITORIAL - 16 CANTONES DE LA PROVINCIA DE LOJA
// Sistema de Referencia: EPSG:4326 (WGS 84) - Zonal 7
// ============================================================================

var cantonesLojaData = {
  "type": "FeatureCollection",
  "name": "Cantones_Provincia_Loja_RVE",
  "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1101",
        "DPA_DESCAN": "LOJA",
        "CABECERA": "Loja",
        "EJE_VIAL": "E35 (San Lucas - Loja - Vilcabamba - Yangana) / E50 (Loja - Catamayo)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.36, -3.72], [-79.12, -3.72], [-79.05, -3.95], [-79.08, -4.35],
          [-79.15, -4.52], [-79.32, -4.50], [-79.38, -4.22], [-79.35, -4.02],
          [-79.42, -3.85], [-79.36, -3.72]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1102",
        "DPA_DESCAN": "CALVAS",
        "CABECERA": "Cariamanga",
        "EJE_VIAL": "E69 (Gonzanamá - Cariamanga - Sozoranga)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.72, -4.18], [-79.48, -4.18], [-79.45, -4.38], [-79.55, -4.48],
          [-79.74, -4.42], [-79.72, -4.18]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1103",
        "DPA_DESCAN": "CATAMAYO",
        "CABECERA": "Catamayo",
        "EJE_VIAL": "E35 / E50 (Loja - Catamayo - San Pedro de la Bendita - Velacruz)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.55, -3.82], [-79.35, -3.82], [-79.32, -4.08], [-79.48, -4.12],
          [-79.58, -4.02], [-79.55, -3.82]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1104",
        "DPA_DESCAN": "CELICA",
        "CABECERA": "Celica",
        "EJE_VIAL": "E25 / E68 (Y de Alamor - Celica - El Empalme)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Excavadora + Volquete + Cuadrilla"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-80.05, -4.02], [-79.82, -4.02], [-79.80, -4.22], [-79.98, -4.28],
          [-80.08, -4.15], [-80.05, -4.02]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1105",
        "DPA_DESCAN": "CHAGUARPAMBA",
        "CABECERA": "Chaguarpamba",
        "EJE_VIAL": "E50 (Río Pindo - Chaguarpamba - Velacruz)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Excavadora + Volquete + Cuadrilla"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.78, -3.76], [-79.55, -3.76], [-79.55, -3.94], [-79.78, -3.94],
          [-79.78, -3.76]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1106",
        "DPA_DESCAN": "ESPINDOLA",
        "CABECERA": "Amaluza",
        "EJE_VIAL": "E69 / Ramal Sur (Cariamanga - Amaluza - Jimbura)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.55, -4.45], [-79.32, -4.45], [-79.30, -4.72], [-79.55, -4.72],
          [-79.55, -4.45]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1107",
        "DPA_DESCAN": "GONZANAMA",
        "CABECERA": "Gonzanamá",
        "EJE_VIAL": "E69 (Catamayo - Nambacola - Gonzanamá - Cariamanga)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Excavadora + Volquete + Cuadrilla"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.58, -4.08], [-79.32, -4.08], [-79.32, -4.30], [-79.56, -4.30],
          [-79.58, -4.08]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1108",
        "DPA_DESCAN": "MACARA",
        "CABECERA": "Macará",
        "EJE_VIAL": "E35 / E69 (El Empalme - Larama - Macará - Sozoranga)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-80.12, -4.25], [-79.82, -4.25], [-79.80, -4.48], [-80.12, -4.48],
          [-80.12, -4.25]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1109",
        "DPA_DESCAN": "PALTAS",
        "CABECERA": "Catacocha",
        "EJE_VIAL": "E35 / E50 (Velacruz - Catacocha - Macandamine - El Empalme)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Excavadora + Volquete + Cuadrilla"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.85, -3.92], [-79.55, -3.92], [-79.55, -4.18], [-79.85, -4.18],
          [-79.85, -3.92]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1110",
        "DPA_DESCAN": "PUYANGO",
        "CABECERA": "Alamor",
        "EJE_VIAL": "E25 (Río Puyango - Y de Alamor - Celica)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Excavadora + Volquete + Cuadrilla"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-80.18, -3.82], [-79.85, -3.82], [-79.85, -4.04], [-80.18, -4.04],
          [-80.18, -3.82]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1111",
        "DPA_DESCAN": "SARAGURO",
        "CABECERA": "Saraguro",
        "EJE_VIAL": "E35 (Límite Azuay/Loja Oña - Saraguro - San Lucas)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.48, -3.38], [-79.08, -3.38], [-79.08, -3.72], [-79.48, -3.72],
          [-79.48, -3.38]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1112",
        "DPA_DESCAN": "SOZORANGA",
        "CABECERA": "Sozoranga",
        "EJE_VIAL": "E69 (Cariamanga - Sozoranga - Sabiango - Macará)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.85, -4.22], [-79.68, -4.22], [-79.68, -4.45], [-79.85, -4.45],
          [-79.85, -4.22]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1113",
        "DPA_DESCAN": "ZAPOTILLO",
        "CABECERA": "Zapotillo",
        "EJE_VIAL": "E25 (Pindal - Sabanilla - Zapotillo - Lalamor)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-80.48, -4.05], [-80.08, -4.05], [-80.08, -4.45], [-80.48, -4.45],
          [-80.48, -4.05]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1114",
        "DPA_DESCAN": "PINDAL",
        "CABECERA": "Pindal",
        "EJE_VIAL": "E25 (Y de Alamor - Pindal - Milagros)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-80.20, -4.02], [-80.02, -4.02], [-80.02, -4.18], [-80.20, -4.18],
          [-80.20, -4.02]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1115",
        "DPA_DESCAN": "QUILANGA",
        "CABECERA": "Quilanga",
        "EJE_VIAL": "Ramal E69 (Gonzanamá - Quilanga - Cariamanga)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.48, -4.25], [-79.32, -4.25], [-79.32, -4.42], [-79.48, -4.42],
          [-79.48, -4.25]
        ]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "DPA_CANTON": "1116",
        "DPA_DESCAN": "OLMEDO",
        "CABECERA": "Olmedo",
        "EJE_VIAL": "E50 (Velacruz - Olmedo - Chaguarpamba)",
        "MAQUINARIA_PERTINENTE": "Retroexcavadora + Volquete + Cuadrilla Microempresa"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[
          [-79.72, -3.90], [-79.58, -3.90], [-79.58, -4.02], [-79.72, -4.02],
          [-79.72, -3.90]
        ]]
      }
    }
  ]
};