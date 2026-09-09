<script lang="ts">
  import { Clipboard, ClipboardCheck } from '@lucide/svelte';
  import { m } from '$lib/paraglide/messages.js';
  import { PCSIZE, BOARDHEIGHT } from '$lib/constants';
  import { getHeight } from '$lib/utils/fumenUtils';
  import type { Fumen } from '$lib/types';
  import { type Page, type Mino, decoder } from 'tetris-fumen';
  import { browser } from '$app/environment';

  export let fumen: string;
  export let clipboard: boolean = true;
  export let minHeight: number = -1;

  let loading: boolean = true;
  let error: string | null = null;

  let imageSrc: string[] | null = null;
  let index: number = 0;

  let showFeedback: boolean = false;
  let feedbackMessage: string = '';

  /**
   * Copies the fumen string to the user's clipboard.
   * Provides visual feedback to the user.
   */
  async function copyContent(): Promise<void> {
    // Check if the Clipboard API is supported by the browser
    if (!navigator.clipboard || !navigator.clipboard.writeText) {
      feedbackMessage = m.copy_not_supported();
      showFeedback = true;
      console.warn('Clipboard API not supported.');
      return;
    }

    try {
      await navigator.clipboard.writeText(fumen);
      feedbackMessage = m.fumen_copied();
      showFeedback = true;
    } catch (err) {
      console.error('Failed to copy content:', err);
      feedbackMessage = m.fumen_copy_failed();
      showFeedback = true;
    } finally {
      // Hide the feedback message after a short delay
      setTimeout(() => {
        showFeedback = false;
        feedbackMessage = '';
      }, 1000); // Display feedback for 1 seconds
    }
  }

  interface BoardStats {
    board: { t: number; c: string }[][];
    tileSize: number;
    style: 'four' | 'fumen';
    lockFlag: boolean;
    grid: {
      fillStyle: string; //turn to BGColor
      strokeStyle: string; //turn to gridColor
    };
  }

  function renderBoardOnCanvas(combinedBoardStats: BoardStats) {
    let tileSize = combinedBoardStats.tileSize;
    let canvas = document.createElement('canvas');
    canvas.width = PCSIZE * tileSize;
    canvas.height = BOARDHEIGHT * tileSize;
    let canvasContext = canvas.getContext('2d');
    if (canvasContext === null) throw new Error('Failed to load fumen: canvas context is null');
    let currentBoard = combinedBoardStats.board;
    type MinoType = 'T' | 'I' | 'L' | 'J' | 'S' | 'Z' | 'X';

    let isFilled = (cell: { t: number; c: string }) => cell.t != 0;

    //base grid
    {
      let gridCvs = document.createElement('canvas');
      gridCvs.height = tileSize;
      gridCvs.width = tileSize;
      let gridCtx = gridCvs.getContext('2d');
      if (gridCtx === null) throw new Error('Failed to load fumen: grid context is null');
      gridCtx.fillStyle = combinedBoardStats.grid.fillStyle;
      gridCtx.fillRect(0, 0, tileSize, tileSize);
      if (combinedBoardStats.grid.strokeStyle.length == 7) {
        //only change opacity if it isn't specified, this keeps tranparent colors unchanged
        gridCtx.strokeStyle = combinedBoardStats.grid.strokeStyle + '60';
      } else {
        gridCtx.strokeStyle = combinedBoardStats.grid.strokeStyle;
      }
      gridCtx.strokeRect(0, 0, tileSize + 1, tileSize + 1);

      // canvasContext.clearRect(0, 0, PCSIZE * tileSize, BOARDHEIGHT * tileSize)
      let gridPattern = canvasContext.createPattern(gridCvs, 'repeat');
      if (gridPattern === null) throw new Error('Failed to load fumen: grid pattern is null');
      canvasContext.fillStyle = gridPattern;
      canvasContext.fillRect(0, 0, PCSIZE * tileSize, BOARDHEIGHT * tileSize);
    }

    fourRender();

    return canvas;

    function fourRender() {
      const FourPalette = {
        normal: {
          T: '#9739a2',
          I: '#42afe1',
          L: '#f38927',
          J: '#1165b5',
          S: '#51b84d',
          Z: '#eb4f65',
          O: '#f6d03c',
          X: '#868686'
        },
        clear: {
          T: '#b94bc6',
          I: '#5cc7f9',
          L: '#f99e4c',
          J: '#2c84da',
          S: '#70d36d',
          Z: '#f96c67',
          O: '#f9df6c',
          X: '#bdbdbd'
        },
        highlight: {
          T: '#d958e9',
          I: '#6ceaff',
          L: '#ffba59',
          J: '#339bff',
          S: '#82f57e',
          Z: '#ff7f79',
          O: '#ffff7f',
          X: '#dddddd'
        }
      };

      // There might be a better way to implement this border priority:
      // 0. background grid
      // 1. border around boundary of filled cells
      // 2. ligher border between filled cells
      // 3. border around highlight
      // The problem comes from 2, which requires checking if both cells neighbouring the border are filled

      const VerticalBorderOpacity: Record<string, string[]> = {
        //left-(border)-right: <cell boarder opacity>-<highlight border opacity>
        '00': ['00', '00'], //empty neighbouring minos
        '11': ['70', '00'], //lighter borders within filled minos
        '01': ['FF', '00'], //boundary of filled cells
        '10': ['FF', '00'],
        '21': ['FF', '00'], //filled cell boundary takes priority over highlight
        '12': ['FF', '00'],
        '20': ['00', 'CC'],
        '02': ['00', 'CC'],
        '22': ['00', 'CC']
      };

      const HorizontalBorderOpacity: Record<string, string[]> = {
        //upper-(border)-lower: <cell boarder opacity>-<highlight border opacity>
        '00': ['00', '00'], //empty neighbouring minos
        '01': ['FF', '00'], //boundary of filled cells
        '10': ['FF', '00'],
        '21': ['FF', '00'],
        '11': ['70', '00'], //lighter borders within filled minos
        '02': ['00', 'CC'], //additional border for highlight
        '12': ['FF', 'CC'],
        //impossible states
        '20': ['00', '00'],
        '22': ['00', '00']
      };

      var foureffectInput = true;

      for (let row = 0; row < currentBoard.length; row++) {
        let displayLineClear = combinedBoardStats.lockFlag && currentBoard[row].every(isFilled);
        for (let col = 0; col < currentBoard[row].length; col++) {
          let cell = currentBoard[row][col];
          let piece = cell.c;

          let cellTypeAbove = currentBoard?.[row - 1]?.[col]?.t ?? 0; // return cell type, defaulting to filled if out of board
          let have3dHighlight = foureffectInput && cellTypeAbove == 0;

          if (cell.t === 2 || (cell.t === 1 && displayLineClear)) {
            if (have3dHighlight)
              draw3dHighlight(col, row, FourPalette.highlight[piece as MinoType]);
            drawMinoRect(col, row, FourPalette.clear[piece as MinoType]);
          } else if (cell.t === 1) {
            if (have3dHighlight)
              draw3dHighlight(col, row, FourPalette.highlight[piece as MinoType]);
            drawMinoRect(col, row, FourPalette.normal[piece as MinoType]);
          }
        }
      }

      function drawMinoRect(x: number, y: number, color: string) {
        canvasContext!.fillStyle = color;
        canvasContext!.fillRect(x * tileSize, y * tileSize, tileSize, tileSize); //copy fumen when grid is specified?
      }

      function draw3dHighlight(x: number, y: number, color: string) {
        //drawn above specified cell
        const highlightSize = tileSize / 5;
        canvasContext!.fillStyle = color;
        canvasContext!.fillRect(
          x * tileSize,
          y * tileSize - highlightSize,
          tileSize,
          highlightSize
        );
      }

      //grid lines for four is more complicated
      var gridSettings = combinedBoardStats.grid;
      if (gridSettings !== undefined) {
        //draw borders according to the surrounding
        for (let row = 0; row < BOARDHEIGHT + 1; row++) {
          for (let col = 0; col < PCSIZE + 1; col++) {
            let leftType = getCellStatus(col - 1, row);
            let rightType = getCellStatus(col, row);

            let resultColors = getColors(VerticalBorderOpacity, leftType, rightType);
            drawVerticalBorder(col, row, resultColors.cellBorderColor, tileSize); //cell
            if (foureffectInput)
              drawVerticalBorder(col, row, resultColors.highlightBorderColor, tileSize / 5); //highlight

            let upperType = getCellStatus(col, row - 1);
            let lowerType = getCellStatus(col, row);

            resultColors = getColors(HorizontalBorderOpacity, upperType, lowerType);
            drawHorizontalBorder(col, row, resultColors.cellBorderColor, 0); //cell
            if (foureffectInput)
              drawHorizontalBorder(
                col,
                row,
                resultColors.highlightBorderColor,
                (1 - 1 / 5) * tileSize
              ); //highlight
          }
        }
      }

      function getColors(
        OpacityTable: Record<string, string[]>,
        firstType: number,
        secondType: number
      ) {
        let BorderOpacities = OpacityTable[String(firstType) + String(secondType)];
        if (gridSettings.strokeStyle.length == 7) {
          //only change opacity if it isn't specified, this keeps tranparent colors unchanged
          return {
            cellBorderColor: gridSettings.strokeStyle + BorderOpacities[0],
            highlightBorderColor: gridSettings.strokeStyle + BorderOpacities[1]
          };
        } else {
          return {
            cellBorderColor: gridSettings.strokeStyle,
            highlightBorderColor: gridSettings.strokeStyle
          };
        }
      }

      function getCellStatus(col: number, row: number) {
        let cellType = currentBoard?.[row]?.[col]?.t ?? 0;
        let cellTypeBelow = currentBoard?.[row + 1]?.[col]?.t ?? 0;
        if (cellType != 0) {
          return 1; //filled cell
        }
        if (cellTypeBelow != 0) {
          return 2; //highlight
        } else {
          return 0; //empty
        }
      }

      //use fillRect instead of strokeRect, as strokeRect is blurry. see: http://diveintohtml5.info/canvas.html#pixel-madness
      function drawVerticalBorder(x: number, y: number, color: string, borderLength: number) {
        //draws left border
        canvasContext!.fillStyle = color;
        canvasContext!.fillRect(
          x * tileSize,
          y * tileSize + (tileSize - borderLength),
          1,
          borderLength
        );
      }

      function drawHorizontalBorder(x: number, y: number, color: string, heightOffset: number) {
        //draws upper border
        canvasContext!.fillStyle = color;
        canvasContext!.fillRect(x * tileSize, y * tileSize + heightOffset, tileSize, 1);
      }
    }
  }

  export function pageToBoard(fumenPage: Page) {
    let fieldString = fumenPage.field.str({ reduced: false, garbage: false }).split('\n');
    fieldString = fieldString.slice(fieldString.length - 20);
    let cellColorToCell = (cellColor: string) =>
      cellColor === '_' ? { t: 0, c: '' } : { t: 1, c: cellColor };
    var newBoard = fieldString.map((rowColors: string) => rowColors.split('').map(cellColorToCell));

    //add glued minos to board
    const operation = fumenPage.operation as Mino;

    if (operation != undefined) {
      let type = operation.type;
      for (let position of operation.positions()) {
        newBoard[19 - position.y][position.x] = { t: 2, c: type }; //operation is bottom-up
      }
    }

    return newBoard;
  }

  function draw(fumenPage: Page, numrows: number) {
    const tileSize = 100;
    const fillStyle = '#00000000';
    const strokeStyle = '#00000000';

    var combinedBoardStats: BoardStats = {
      board: pageToBoard(fumenPage),
      tileSize: tileSize,
      style: 'four',
      lockFlag: false,
      grid: {
        fillStyle: fillStyle, //turn to BGColor
        strokeStyle: strokeStyle //turn to gridColor
      }
    };

    var canvas = document.createElement('canvas');
    canvas.width = PCSIZE * tileSize;
    canvas.height = numrows * tileSize;

    const canvasContext = canvas.getContext('2d');
    if (canvasContext === null) {
      throw new Error('Failed to load fumen: context was null');
    }

    canvasContext.imageSmoothingEnabled = false; // no anti-aliasing
    canvasContext.drawImage(
      renderBoardOnCanvas(combinedBoardStats),
      0,
      -20 * tileSize + canvas.height
    );

    //add surrounding border
    canvasContext.strokeStyle = strokeStyle;
    canvasContext.strokeRect(0.5, 0.5, canvas.width - 1, canvas.height - 1);

    return canvas;
  }

  function fumencanvas(fumen: Fumen) {
    var resultURLs = [];

    const pages = decoder.decode(fumen);
    const height = Math.max(getHeight(fumen) + 1, minHeight + 1);

    for (let page of pages) {
      let canvas = draw(page, height);
      var data_url = canvas.toDataURL('image/png');

      var img = new Image();
      img.classList.add('imageOutput', 'fourImageOutput');
      img.src = data_url;

      resultURLs.push(data_url);
    }

    return { resultURLs };
  }

  async function renderImages(fumen: Fumen) {
    fumen = fumen.replace(/[Ddm]115@/gm, 'v115@') as Fumen;
    let { resultURLs } = fumencanvas(fumen);
    imageSrc = resultURLs;
  }

  async function loadFumen() {
    try {
      await renderImages(fumen as Fumen);
    } catch (e: unknown) {
      error = (e as Error).message;
      console.error('Error fetching or processing image:', e);
    } finally {
      loading = false;
    }
  }

  $: if (browser && fumen) loadFumen();
</script>

<div class="group border-base-200 bg-base-200 relative h-auto w-full rounded-md border p-4">
  {#if loading && fumen}
    <div class="flex aspect-[5/2] items-center justify-center">
      <p>{m.loading_image()}</p>
    </div>
  {:else if error}
    <div class="flex aspect-[5/2] items-center justify-center">
      <p>{m.error()}: {error}</p>
    </div>
  {:else if imageSrc}
    <img class="h-auto w-full" src={imageSrc[index]} alt={fumen} />

    <!-- Buttons -->
    {#if index > 0}
      <button
        id="prev"
        class="absolute top-1/2 left-3 -translate-y-1/2 rounded-full bg-black/20 p-2 text-white hover:cursor-pointer hover:bg-black/50"
        on:click={() => index--}
      >
        &#10094;
      </button>
    {/if}
    {#if index < imageSrc.length - 1}
      <button
        id="next"
        class="absolute top-1/2 right-3 -translate-y-1/2 rounded-full bg-black/20 p-2 text-white hover:cursor-pointer hover:bg-black/50"
        on:click={() => index++}
      >
        &#10095;
      </button>
    {/if}

    {#if clipboard}
      <div
        class={'transparent absolute top-[10px] right-[10px] z-20 rounded-md opacity-0 transition-opacity duration-300 group-hover:opacity-100 ' +
          (showFeedback ? 'bg-base-300' : '')}
        class:border={showFeedback}
      >
        <div class="flex justify-end">
          {#if showFeedback}
            <span class="h-full p-2" class:show={showFeedback}>
              {feedbackMessage}
            </span>
          {/if}

          <button
            class="bg-base-300 cursor-pointer rounded-md border p-2 opacity-50 hover:opacity-80"
            class:border={!showFeedback}
            on:click={copyContent}
          >
            {#if showFeedback}
              <ClipboardCheck class="text-base-content" />
            {:else}
              <Clipboard class="text-base-content" />
            {/if}
          </button>
        </div>
      </div>
    {/if}
  {:else}
    <p></p>
  {/if}
</div>
