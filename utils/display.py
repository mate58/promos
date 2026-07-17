from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box

def display_promotions(promotions_by_bank: dict):
    console = Console()
    
    # Título principal con Panel
    title = Panel(
        Align.center(
            "[bold green]📢 CONTROL DE BENEFICIOS Y PROMOCIONES DE TRANSPORTE 🚌🚇[/bold green]\n"
            "[dim]Colectivos y Subtes (CABA y AMBA) - Julio 2026[/dim]"
        ),
        box=box.ROUNDED,
        border_style="green",
        expand=False
    )
    console.print(title)
    console.print()
    
    for bank_name, promos in promotions_by_bank.items():
        if not promos:
            continue
            
        # Creación de tabla para cada banco/entidad
        table = Table(
            title=f"[bold cyan]🏦 {bank_name.upper()}[/bold cyan]",
            title_justify="left",
            box=box.ROUNDED,
            border_style="blue",
            expand=True
        )
        
        table.add_column("Beneficio / Promo", style="yellow", ratio=2)
        table.add_column("Días", style="magenta", ratio=1)
        table.add_column("Tope", style="green", ratio=1)
        table.add_column("Descripción y Requisitos", style="white", ratio=3)
        table.add_column("Tipo", style="cyan", ratio=1)
        table.add_column("Origen", ratio=1)
        
        for promo in promos:
            source = promo.get("fuente", "Local")
            source_style = "[bold green]En Vivo (Web)[/bold green]" if "Vivo" in source else "[bold blue]Local (Estable)[/bold blue]"
            
            req_str = f"\n[dim]Req: {promo.get('requisitos', '')}[/dim]" if promo.get('requisitos') else ""
            desc_text = f"{promo.get('descripcion', '')}{req_str}"
            
            table.add_row(
                promo.get("titulo", "N/D"),
                promo.get("dias", "N/D"),
                promo.get("tope", "N/D"),
                desc_text,
                promo.get("tipo", "N/D"),
                source_style
            )
            
        console.print(table)
        console.print()
        
    console.print("[dim italic]Nota: Las promociones pueden requerir validaciones o registrar saldo. Siempre consulta con las aplicaciones oficiales de las entidades.[/dim italic]")
