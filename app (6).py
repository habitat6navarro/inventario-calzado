"""
╔══════════════════════════════════════════════════════════════╗
║       SISTEMA DE INVENTARIO DE CALZADO - Calzados La 40      ║
║       Desarrollado con Python, Streamlit y Supabase           ║
╚══════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Calzados La 40 · Inventario",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');
    .stApp { background: #0f0f0f; color: #f0ece4; }
    [data-testid="stSidebar"] { background: #1a1a1a; border-right: 1px solid #2a2a2a; }
    [data-testid="stSidebar"] * { color: #f0ece4 !important; }
    h1, h2, h3 { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 2px; }
    body, p, div, span, label { font-family: 'DM Sans', sans-serif !important; }
    .brand-header {
        font-family: 'Bebas Neue', sans-serif; font-size: 3.2rem; letter-spacing: 6px;
        background: linear-gradient(135deg, #f0ece4 0%, #c8a96e 50%, #f0ece4 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0; line-height: 1;
    }
    .brand-sub { font-family: 'DM Sans', sans-serif; font-size: 0.75rem; letter-spacing: 4px; color: #666; text-transform: uppercase; margin-top: 4px; }
    .metric-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 12px; padding: 20px 24px; position: relative; overflow: hidden; transition: border-color 0.3s; }
    .metric-card:hover { border-color: #c8a96e; }
    .metric-card::before { content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: linear-gradient(180deg, #c8a96e, #8b6914); }
    .metric-label { font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; color: #666; margin-bottom: 8px; }
    .metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.8rem; color: #f0ece4; line-height: 1; }
    .metric-value.danger { color: #e05555; }
    .metric-value.warning { color: #e0a455; }
    .metric-value.success { color: #55c075; }
    .alert-box { background: rgba(224,85,85,0.08); border: 1px solid rgba(224,85,85,0.3); border-radius: 10px; padding: 14px 18px; margin: 6px 0; font-size: 0.85rem; color: #e05555; }
    .alert-box span { font-weight: 600; }
    .dataframe { background: #1a1a1a !important; color: #f0ece4 !important; }
    .stSelectbox > div > div, .stNumberInput > div > div > input { background: #1a1a1a !important; border: 1px solid #2a2a2a !important; color: #f0ece4 !important; border-radius: 8px !important; }
    .stTextInput > div > div > input { background: #1a1a1a !important; border: 1px solid #2a2a2a !important; color: #f0ece4 !important; border-radius: 8px !important; }
    .stButton > button { background: linear-gradient(135deg, #c8a96e, #8b6914) !important; color: #0f0f0f !important; border: none !important; border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; letter-spacing: 1px !important; padding: 10px 24px !important; transition: opacity 0.2s !important; }
    .stButton > button:hover { opacity: 0.85 !important; }
    hr { border: none; border-top: 1px solid #2a2a2a; margin: 24px 0; }
    .section-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.6rem; letter-spacing: 3px; color: #c8a96e; border-bottom: 1px solid #2a2a2a; padding-bottom: 8px; margin-bottom: 16px; }
    .size-badge { display: inline-block; background: #2a2a2a; color: #c8a96e; border: 1px solid #c8a96e; border-radius: 6px; padding: 2px 10px; font-size: 0.8rem; font-weight: 600; margin: 2px; }
    .size-badge.out { border-color: #e05555; color: #e05555; background: rgba(224,85,85,0.08); }
    .msg-success { background: rgba(85,192,117,0.1); border: 1px solid rgba(85,192,117,0.4); border-radius: 10px; padding: 14px 18px; color: #55c075; font-weight: 500; }
    .msg-error { background: rgba(224,85,85,0.1); border: 1px solid rgba(224,85,85,0.4); border-radius: 10px; padding: 14px 18px; color: #e05555; font-weight: 500; }
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CONEXIÓN A SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()


# ─────────────────────────────────────────────
#  HELPERS DE CONSULTA
# ─────────────────────────────────────────────
def get_productos():
    res = supabase.table("productos").select("*").order("marca").order("referencia").execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def get_inventario_full():
    res = supabase.table("inventario").select(
        "talla, stock, productos(id, marca, referencia, precio_costo, precio_venta)"
    ).execute()
    if not res.data:
        return pd.DataFrame()
    rows = []
    for r in res.data:
        p = r["productos"]
        rows.append({
            "marca": p["marca"], "referencia": p["referencia"],
            "talla": r["talla"], "stock": r["stock"],
            "precio_costo": p["precio_costo"], "precio_venta": p["precio_venta"],
            "valor_total": r["stock"] * p["precio_venta"], "producto_id": p["id"],
        })
    return pd.DataFrame(rows).sort_values(["marca","referencia","talla"])

def get_tallas_por_producto(producto_id):
    res = supabase.table("inventario").select("talla,stock").eq("producto_id", producto_id).order("talla").execute()
    return res.data or []

def get_stock_talla(producto_id, talla):
    res = supabase.table("inventario").select("stock").eq("producto_id", producto_id).eq("talla", talla).execute()
    return res.data[0]["stock"] if res.data else 0

def registrar_movimiento(producto_id, talla, tipo, cantidad, notas=""):
    try:
        res = supabase.table("inventario").select("stock").eq("producto_id", producto_id).eq("talla", talla).execute()
        if not res.data:
            if tipo != "ENTRADA":
                return False, "La talla no existe en el inventario."
            supabase.table("inventario").insert({"producto_id": producto_id, "talla": talla, "stock": 0}).execute()
            stock_antes = 0
        else:
            stock_antes = res.data[0]["stock"]
        if tipo == "VENTA":
            if stock_antes < cantidad:
                return False, f"Stock insuficiente. Disponible: {stock_antes} par(es), solicitado: {cantidad}."
            stock_nuevo = stock_antes - cantidad
        elif tipo == "ENTRADA":
            stock_nuevo = stock_antes + cantidad
        else:
            stock_nuevo = max(0, stock_antes + cantidad)
        supabase.table("inventario").update({"stock": stock_nuevo}).eq("producto_id", producto_id).eq("talla", talla).execute()
        supabase.table("historial_movimientos").insert({
            "producto_id": producto_id, "talla": talla, "tipo": tipo,
            "cantidad": cantidad, "stock_antes": stock_antes, "stock_despues": stock_nuevo, "notas": notas,
        }).execute()
        return True, f"✓ {tipo} registrada. Stock {stock_antes} → {stock_nuevo} par(es)."
    except Exception as e:
        return False, f"Error: {e}"

def agregar_producto(referencia, marca, descripcion, precio_costo, precio_venta):
    if not referencia.strip():
        return False, "La referencia no puede estar vacía."
    try:
        supabase.table("productos").insert({
            "referencia": referencia.strip(), "marca": marca.strip(),
            "descripcion": descripcion.strip(), "precio_costo": precio_costo, "precio_venta": precio_venta,
        }).execute()
        return True, f"Producto '{referencia}' creado exitosamente."
    except Exception as e:
        return False, f"Error al crear producto: {e}"

def editar_producto(producto_id, referencia, marca, descripcion, precio_costo, precio_venta):
    if not referencia.strip():
        return False, "La referencia no puede estar vacía."
    try:
        supabase.table("productos").update({
            "referencia": referencia.strip(), "marca": marca.strip(),
            "descripcion": descripcion.strip(), "precio_costo": precio_costo, "precio_venta": precio_venta,
        }).eq("id", producto_id).execute()
        return True, "✓ Producto actualizado correctamente."
    except Exception as e:
        return False, f"Error al actualizar: {e}"

def eliminar_producto(producto_id):
    try:
        res = supabase.table("productos").select("referencia").eq("id", producto_id).execute()
        if not res.data:
            return False, "Producto no encontrado."
        nombre = res.data[0]["referencia"]
        supabase.table("historial_movimientos").delete().eq("producto_id", producto_id).execute()
        supabase.table("inventario").delete().eq("producto_id", producto_id).execute()
        supabase.table("productos").delete().eq("id", producto_id).execute()
        return True, f"✓ '{nombre}' eliminado junto con su inventario e historial."
    except Exception as e:
        return False, f"Error al eliminar: {e}"

def get_historial(limit=100):
    res = supabase.table("historial_movimientos").select(
        "fecha, tipo, talla, cantidad, stock_antes, stock_despues, notas, productos(marca, referencia)"
    ).order("fecha", desc=True).limit(limit).execute()
    if not res.data:
        return pd.DataFrame()
    rows = []
    for r in res.data:
        p = r["productos"]
        rows.append({
            "fecha": r["fecha"], "marca": p["marca"], "referencia": p["referencia"],
            "talla": r["talla"], "tipo": r["tipo"], "cantidad": r["cantidad"],
            "stock_antes": r["stock_antes"], "stock_despues": r["stock_despues"],
            "notas": r["notas"] or "",
        })
    return pd.DataFrame(rows)

def get_dashboard_stats():
    inv = supabase.table("inventario").select("stock, productos(precio_venta)").execute()
    prods = supabase.table("productos").select("id").execute()
    total_refs  = len(prods.data)
    total_pares = sum(r["stock"] for r in inv.data)
    tallas_agot = sum(1 for r in inv.data if r["stock"] == 0)
    valor_inv   = sum(r["stock"] * r["productos"]["precio_venta"] for r in inv.data)
    agotadas = supabase.table("inventario").select("talla, productos(referencia)").eq("stock", 0).limit(20).execute()
    agotadas_det = [{"referencia": r["productos"]["referencia"], "talla": r["talla"]} for r in agotadas.data]
    return {"total_refs": total_refs, "total_pares": total_pares,
            "tallas_agotadas": tallas_agot, "valor_inventario": valor_inv,
            "agotadas_detalle": agotadas_det}


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 24px 0'>
        <div class='brand-header'>CALZADOS<br>LA 40</div>
        <div class='brand-sub'>Sistema de Inventario</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    pagina = st.radio("Navegación",
        ["📊  Dashboard","📦  Inventario","🔄  Movimientos","➕  Nuevo Producto","📋  Historial"],
        label_visibility="collapsed")
    pagina = pagina.split("  ")[1]
    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("☁ Base de datos: Supabase\nDatos persistentes en la nube")


# ─────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────
if pagina == "Dashboard":
    st.markdown("<div class='brand-header' style='font-size:2.2rem'>DASHBOARD</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>RESUMEN GENERAL DEL ALMACÉN</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.spinner("Cargando datos..."):
        stats = get_dashboard_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Referencias</div><div class='metric-value'>{stats['total_refs']}</div></div>", unsafe_allow_html=True)
    with col2:
        cls = "warning" if stats["total_pares"] < 50 else "success"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Pares en Bodega</div><div class='metric-value {cls}'>{stats['total_pares']}</div></div>", unsafe_allow_html=True)
    with col3:
        cls = "danger" if stats["tallas_agotadas"] > 5 else ("warning" if stats["tallas_agotadas"] > 0 else "success")
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Tallas Agotadas</div><div class='metric-value {cls}'>{stats['tallas_agotadas']}</div></div>", unsafe_allow_html=True)
    with col4:
        valor = stats['valor_inventario']
        vf = f"$ COP {valor:,.0f}" if valor < 1_000_000 else f"$ COP {valor/1_000_000:.1f}M"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Valor Inventario</div><div class='metric-value' style='font-size:1.6rem'>{vf}</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1.5, 1])
    with col_a:
        st.markdown("<div class='section-title'>STOCK POR REFERENCIA</div>", unsafe_allow_html=True)
        inv = get_inventario_full()
        if not inv.empty:
            resumen = inv.groupby("referencia")["stock"].sum().reset_index().sort_values("stock")
            st.bar_chart(resumen.set_index("referencia")["stock"], color="#c8a96e", height=320)
    with col_b:
        st.markdown("<div class='section-title'>⚠ ALERTAS DE AGOTADO</div>", unsafe_allow_html=True)
        if stats["agotadas_detalle"]:
            for row in stats["agotadas_detalle"]:
                st.markdown(f"<div class='alert-box'><span>{row['referencia']}</span> — Talla {row['talla']}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='msg-success'>✓ Todas las tallas tienen stock disponible.</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  INVENTARIO
# ─────────────────────────────────────────────
elif pagina == "Inventario":
    st.markdown("<div class='brand-header' style='font-size:2.2rem'>INVENTARIO</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>TABLA DE STOCK EN BODEGA</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    with st.spinner("Cargando inventario..."):
        inv   = get_inventario_full()
        prods = get_productos()
    if inv.empty:
        st.info("No hay productos registrados aún.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            marcas = ["Todas"] + sorted(inv["marca"].unique().tolist())
            filtro_marca = st.selectbox("Filtrar por Marca", marcas)
        with col2:
            tallas_disp = ["Todas"] + sorted(inv["talla"].unique().tolist())
            filtro_talla = st.selectbox("Filtrar por Talla", tallas_disp)
        with col3:
            solo_stock = st.checkbox("Solo con stock disponible", value=False)
        df_f = inv.copy()
        if filtro_marca != "Todas": df_f = df_f[df_f["marca"] == filtro_marca]
        if filtro_talla != "Todas": df_f = df_f[df_f["talla"] == filtro_talla]
        if solo_stock: df_f = df_f[df_f["stock"] > 0]
        st.markdown(f"<br>Mostrando **{len(df_f)}** registros<br>", unsafe_allow_html=True)
        df_show = df_f.copy()
        df_show["talla"]        = df_show["talla"].apply(lambda x: f"{x:.0f}")
        df_show["precio_costo"] = df_show["precio_costo"].apply(lambda x: f"$ COP {x:,.0f}")
        df_show["precio_venta"] = df_show["precio_venta"].apply(lambda x: f"$ COP {x:,.0f}")
        df_show["valor_total"]  = df_show["valor_total"].apply(lambda x: f"$ COP {x:,.0f}")
        df_show = df_show[["marca","referencia","talla","stock","precio_costo","precio_venta","valor_total"]]
        df_show.columns = ["Marca","Referencia","Talla","Stock","Costo","P. Venta","Valor Total"]
        def color_stock(val):
            try:
                v = int(val)
                if v == 0:   return "background-color: rgba(224,85,85,0.15); color: #e05555;"
                elif v <= 3: return "background-color: rgba(224,164,85,0.15); color: #e0a455;"
                return ""
            except: return ""
        st.dataframe(df_show.style.map(color_stock, subset=["Stock"]), use_container_width=True, hide_index=True, height=420)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>GESTIÓN DE PRODUCTOS</div>", unsafe_allow_html=True)
        st.caption("Haz clic en ✏ Editar o 🗑 Eliminar en la tarjeta del producto que quieres modificar.")
        if "inv_accion" not in st.session_state:
            st.session_state.inv_accion = None
        for _, prod in prods.iterrows():
            tallas = get_tallas_por_producto(prod["id"])
            badges = "".join(
                f"<span class='size-badge{'' if t['stock'] > 0 else ' out'}'>{t['talla']:.0f} <small>({t['stock']})</small></span> "
                for t in sorted(tallas, key=lambda x: x["talla"])
            )
            col_info, col_btns = st.columns([5, 1])
            with col_info:
                st.markdown(f"""
                <div style='padding:12px 16px 10px 16px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:10px;margin-bottom:2px'>
                    <div style='font-size:0.68rem;letter-spacing:2px;color:#666;text-transform:uppercase'>{prod['marca']}</div>
                    <div style='font-weight:600;font-size:1rem;color:#f0ece4;margin:2px 0 6px 0'>{prod['referencia']}</div>
                    <div style='font-size:0.78rem;color:#888;margin-bottom:8px'>
                        Costo: <b style='color:#c8a96e'>$ COP {prod['precio_costo']:,.0f}</b> &nbsp;·&nbsp;
                        Venta: <b style='color:#c8a96e'>$ COP {prod['precio_venta']:,.0f}</b> &nbsp;·&nbsp;
                        {prod['descripcion'] if prod['descripcion'] else '—'}
                    </div>
                    <div>{badges if badges else '<span style="color:#555;font-size:0.8rem">Sin tallas</span>'}</div>
                </div>""", unsafe_allow_html=True)
            with col_btns:
                st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
                if st.button("✏ Editar", key=f"edit_{prod['id']}"):
                    st.session_state.inv_accion = None if st.session_state.inv_accion == ("editar", prod["id"]) else ("editar", prod["id"])
                    st.rerun()
                if st.button("🗑 Eliminar", key=f"del_{prod['id']}"):
                    st.session_state.inv_accion = None if st.session_state.inv_accion == ("eliminar", prod["id"]) else ("eliminar", prod["id"])
                    st.rerun()
            if st.session_state.inv_accion == ("editar", prod["id"]):
                with st.container():
                    ec1, ec2, ec3 = st.columns(3)
                    with ec1:
                        e_ref   = st.text_input("Referencia", value=prod["referencia"], key=f"eref_{prod['id']}")
                        e_marca = st.text_input("Marca",      value=prod["marca"],      key=f"emarca_{prod['id']}")
                    with ec2:
                        e_desc  = st.text_input("Descripción", value=prod["descripcion"] or "", key=f"edesc_{prod['id']}")
                        e_costo = st.number_input("Precio Costo ($)", min_value=0.0, value=float(prod["precio_costo"]), step=1000.0, format="%.0f", key=f"ecosto_{prod['id']}")
                    with ec3:
                        e_pventa = st.number_input("Precio Venta ($)", min_value=0.0, value=float(prod["precio_venta"]), step=1000.0, format="%.0f", key=f"epventa_{prod['id']}")
                        if e_costo > 0 and e_pventa > 0:
                            m = ((e_pventa - e_costo) / e_pventa) * 100
                            st.markdown(f"<div style='margin-top:8px;font-size:0.8rem;color:#666'>Margen: <b style='color:{'#55c075' if m>=30 else '#e0a455'}'>{m:.1f}%</b></div>", unsafe_allow_html=True)
                    sb1, sb2 = st.columns([1, 4])
                    with sb1:
                        if st.button("💾 Guardar", key=f"save_{prod['id']}"):
                            ok, msg = editar_producto(prod["id"], e_ref, e_marca, e_desc, e_costo, e_pventa)
                            if ok:
                                st.session_state.inv_accion = None
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    with sb2:
                        if st.button("✕ Cancelar", key=f"cancel_edit_{prod['id']}"):
                            st.session_state.inv_accion = None
                            st.rerun()
            elif st.session_state.inv_accion == ("eliminar", prod["id"]):
                tallas_p = get_tallas_por_producto(prod["id"])
                total_p  = sum(t["stock"] for t in tallas_p)
                n_movs   = supabase.table("historial_movimientos").select("id", count="exact").eq("producto_id", prod["id"]).execute().count or 0
                st.warning(f"⚠ Esto borrará permanentemente **{prod['referencia']}** — {len(tallas_p)} tallas, {total_p} pares, {n_movs} movimientos. Esta acción es irreversible.")
                db1, db2 = st.columns([1, 4])
                with db1:
                    if st.button("🗑 Sí, eliminar", key=f"confirm_del_{prod['id']}"):
                        ok, msg = eliminar_producto(prod["id"])
                        if ok:
                            st.session_state.inv_accion = None
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with db2:
                    if st.button("✕ Cancelar", key=f"cancel_del_{prod['id']}"):
                        st.session_state.inv_accion = None
                        st.rerun()


# ─────────────────────────────────────────────
#  MOVIMIENTOS
# ─────────────────────────────────────────────
elif pagina == "Movimientos":
    st.markdown("<div class='brand-header' style='font-size:2.2rem'>MOVIMIENTOS</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>ENTRADAS · VENTAS · AJUSTES</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    prods = get_productos()
    if prods.empty:
        st.warning("Primero debes agregar productos en 'Nuevo Producto'.")
        st.stop()
    st.markdown("<div class='section-title'>REGISTRAR MOVIMIENTO</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        tipo_mov = st.selectbox("Tipo de Movimiento", ["ENTRADA","VENTA","AJUSTE"])
        opciones_prod = {f"{r['marca']} — {r['referencia']}": r["id"] for _, r in prods.iterrows()}
        sel_prod_label = st.selectbox("Referencia / Producto", list(opciones_prod.keys()))
        producto_id = opciones_prod[sel_prod_label]
        tallas_inv  = get_tallas_por_producto(producto_id)
        sel_talla   = None
        if tipo_mov == "ENTRADA":
            nueva_talla_str = st.text_input("Talla (existente o nueva)", placeholder="Ej: 38")
            if nueva_talla_str.strip():
                try:    sel_talla = float(nueva_talla_str.strip().replace(",", "."))
                except: st.error("Ingresa un número de talla válido.")
        else:
            if not tallas_inv:
                st.warning("Este producto no tiene tallas registradas.")
                st.stop()
            tallas_lista = [t for t in tallas_inv if t["stock"] > 0] if tipo_mov == "VENTA" else tallas_inv
            if tipo_mov == "VENTA" and not tallas_lista:
                st.markdown("<div class='msg-error'>⚠ No hay stock disponible en ninguna talla.</div>", unsafe_allow_html=True)
                st.stop()
            tallas_dict = {f"Talla {t['talla']:.0f}  (Stock: {t['stock']} pares)": t["talla"] for t in sorted(tallas_lista, key=lambda x: x["talla"])}
            sel_talla = tallas_dict[st.selectbox("Talla", list(tallas_dict.keys()))]
    with col2:
        if sel_talla is not None:
            stock_actual = get_stock_talla(producto_id, sel_talla)
            st.markdown(f"""
            <div class='metric-card' style='margin-top:28px'>
                <div class='metric-label'>Stock Actual — Talla {sel_talla:.0f}</div>
                <div class='metric-value {"danger" if stock_actual==0 else "success"}'>{stock_actual}</div>
                <div style='color:#666;font-size:0.75rem;margin-top:4px'>pares disponibles</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if tipo_mov == "AJUSTE":
            cantidad = st.number_input("Cantidad (+ añadir, − descontar)", min_value=-9999, max_value=9999, value=0, step=1)
        else:
            cantidad = st.number_input("Cantidad de Pares", min_value=1, max_value=9999, value=1, step=1)
        notas = st.text_input("Notas (opcional)", placeholder="Ej: Proveedor XYZ, Factura #123")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(f"✓ Registrar {tipo_mov}", use_container_width=True):
        if sel_talla is None:
            st.markdown("<div class='msg-error'>⚠ Debes especificar una talla válida.</div>", unsafe_allow_html=True)
        elif cantidad == 0 and tipo_mov == "AJUSTE":
            st.markdown("<div class='msg-error'>⚠ La cantidad de ajuste no puede ser 0.</div>", unsafe_allow_html=True)
        else:
            ok, msg = registrar_movimiento(producto_id, sel_talla, tipo_mov, cantidad, notas)
            if ok:
                st.markdown(f"<div class='msg-success'>{msg}</div>", unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"<div class='msg-error'>⚠ {msg}</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  NUEVO PRODUCTO
# ─────────────────────────────────────────────
elif pagina == "Nuevo Producto":
    st.markdown("<div class='brand-header' style='font-size:2.2rem'>NUEVO PRODUCTO</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>AGREGAR REFERENCIA AL CATÁLOGO</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>DATOS DE LA REFERENCIA</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        referencia  = st.text_input("Referencia *", placeholder="Ej: Adidas Superstar")
        marca       = st.text_input("Marca *",       placeholder="Ej: Adidas")
        descripcion = st.text_input("Descripción",   placeholder="Ej: Cuero blanco, suela Shell")
    with col2:
        precio_costo = st.number_input("Precio de Costo ($)", min_value=0.0, step=1000.0, format="%.0f")
        precio_venta = st.number_input("Precio de Venta ($)", min_value=0.0, step=1000.0, format="%.0f")
        if precio_costo > 0 and precio_venta > 0:
            margen = ((precio_venta - precio_costo) / precio_venta) * 100
            st.markdown(f"""
            <div class='metric-card' style='margin-top:8px'>
                <div class='metric-label'>Margen de Ganancia</div>
                <div class='metric-value {"success" if margen>=30 else "warning"}'>{margen:.1f}%</div>
            </div>""", unsafe_allow_html=True)
    st.markdown("<br><div class='section-title'>TALLAS INICIALES (Opcional)</div>", unsafe_allow_html=True)
    st.caption("Puedes agregar tallas ahora o después en Movimientos → ENTRADA")
    tallas_input = st.multiselect("Selecciona las tallas disponibles", options=[34,35,36,37,38,39,40,41,42,43,44,45], default=[38,39,40,41,42])
    stock_inicial = {}
    if tallas_input:
        cols = st.columns(min(len(tallas_input), 6))
        for i, talla in enumerate(sorted(tallas_input)):
            with cols[i % 6]:
                stock_inicial[talla] = st.number_input(f"T. {talla}", min_value=0, max_value=999, value=0, step=1, key=f"si_{talla}")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✓ Crear Producto", use_container_width=True):
        ok, msg = agregar_producto(referencia, marca, descripcion, precio_costo, precio_venta)
        if ok:
            st.markdown(f"<div class='msg-success'>{msg}</div>", unsafe_allow_html=True)
            if tallas_input:
                res = supabase.table("productos").select("id").eq("referencia", referencia.strip()).order("id", desc=True).limit(1).execute()
                pid = res.data[0]["id"]
                for t in sorted(tallas_input):
                    s = stock_inicial.get(t, 0)
                    supabase.table("inventario").insert({"producto_id": pid, "talla": t, "stock": s}).execute()
                    if s > 0:
                        registrar_movimiento(pid, t, "ENTRADA", s, "Stock inicial al crear producto")
            st.balloons()
        else:
            st.markdown(f"<div class='msg-error'>⚠ {msg}</div>", unsafe_allow_html=True)
    st.markdown("<br><div class='section-title'>CATÁLOGO ACTUAL</div>", unsafe_allow_html=True)
    prods = get_productos()
    if not prods.empty:
        df_show = prods[["marca","referencia","precio_costo","precio_venta","creado_en"]].copy()
        df_show["precio_costo"] = df_show["precio_costo"].apply(lambda x: f"$ COP {x:,.0f}")
        df_show["precio_venta"] = df_show["precio_venta"].apply(lambda x: f"$ COP {x:,.0f}")
        df_show.columns = ["Marca","Referencia","Costo","P. Venta","Creado"]
        st.dataframe(df_show, use_container_width=True, hide_index=True)
    else:
        st.info("No hay productos creados aún.")


# ─────────────────────────────────────────────
#  HISTORIAL
# ─────────────────────────────────────────────
elif pagina == "Historial":
    st.markdown("<div class='brand-header' style='font-size:2.2rem'>HISTORIAL</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-sub'>REGISTRO DE TODOS LOS MOVIMIENTOS</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1: filtro_tipo = st.selectbox("Tipo", ["TODOS","ENTRADA","VENTA","AJUSTE"])
    with col2: limite = st.selectbox("Mostrar últimos", [50,100,200,500], index=1)
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        exportar = st.button("⬇ Exportar CSV")
    with st.spinner("Cargando historial..."):
        hist = get_historial(limit=limite)
    if filtro_tipo != "TODOS" and not hist.empty:
        hist = hist[hist["tipo"] == filtro_tipo]
    if exportar and not hist.empty:
        st.download_button("📥 Descargar CSV", hist.to_csv(index=False).encode("utf-8"), "historial.csv", "text/csv")
    st.markdown(f"<br>**{len(hist)}** registros encontrados<br>", unsafe_allow_html=True)
    if hist.empty:
        st.info("No hay movimientos registrados.")
    else:
        df_hist = hist.copy()
        df_hist["tipo"]        = df_hist["tipo"].map({"ENTRADA":"📥 ENTRADA","VENTA":"🛒 VENTA","AJUSTE":"⚙ AJUSTE"})
        df_hist["talla"]       = df_hist["talla"].apply(lambda x: f"{x:.0f}")
        df_hist["movimiento"]  = df_hist.apply(lambda r: f'+{int(r["cantidad"])}' if "ENTRADA" in str(r["tipo"]) else (f'−{int(r["cantidad"])}' if "VENTA" in str(r["tipo"]) else f'~{int(r["cantidad"])}'), axis=1)
        df_hist["stock_cambio"]= df_hist.apply(lambda r: f'{int(r["stock_antes"])} → {int(r["stock_despues"])}', axis=1)
        df_hist["notas"]       = df_hist["notas"].fillna("—").replace("", "—")
        df_show = df_hist[["fecha","marca","referencia","talla","tipo","movimiento","stock_cambio","notas"]].copy()
        df_show.columns = ["Fecha","Marca","Referencia","Talla","Tipo","Cantidad","Stock antes→después","Notas"]
        def color_tipo(val):
            if "ENTRADA" in str(val): return "color: #55c075;"
            elif "VENTA"  in str(val): return "color: #e05555;"
            elif "AJUSTE" in str(val): return "color: #c8a96e;"
            return ""
        st.dataframe(df_show.style.map(color_tipo, subset=["Tipo"]), use_container_width=True, hide_index=True, height=520)
